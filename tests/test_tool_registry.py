"""
Tests for PanelRegistry.get_tools_for_user().

Key behaviours covered:
- returns an empty dict when no panels are registered
- panels without get_config() expose no tools (legacy backwards-compat)
- tools are namespaced as <panel_id>__<tool_name>
- result values are (panel, tool) tuples
- multiple tools from one panel all appear
- tools from multiple panels all appear
- REQUIRE_SUPERUSER tools are hidden from non-superusers
- REQUIRE_SUPERUSER tools are visible to superusers
- a panel whose get_config() raises does not prevent other panels' tools loading
- a panel whose config.tools raises on iteration does not prevent other panels' tools loading
- a panel whose _check_permission() raises does not prevent other panels' tools loading
- a warning is logged for each panel that fails, not silently swallowed
"""

from django.test import TestCase

from dj_control_room.registry import PanelRegistry


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_tool(name="do_thing", scope="view"):
    """Return a minimal PanelTool."""
    from dj_control_room_base.core.panel_tool import PanelTool

    return PanelTool(
        name=name,
        scope=scope,
        description="A test tool",
        input_schema={"type": "object", "properties": {}},
        handler=lambda ctx: None,
    )


def _make_config(tools=None, require_superuser=False):
    """Return a PanelConfig with the given tools list."""
    from dj_control_room_base.core import PanelConfig

    return PanelConfig(
        settings_key="DJ_NONEXISTENT_SETTINGS",
        defaults={"REQUIRE_SUPERUSER": require_superuser},
        tools=tools or [],
    )


class _PanelWithTools:
    name = "Tool Panel"
    description = "Panel that exposes tools"
    icon = "wrench"

    def __init__(self, tools=None, require_superuser=False):
        self._config = _make_config(tools=tools, require_superuser=require_superuser)

    def get_config(self):
        return self._config


class _PanelGetConfigRaises:
    name = "Broken Config Panel"
    description = "get_config() always raises"
    icon = "x"

    def get_config(self):
        raise RuntimeError("simulated get_config failure")


class _PanelToolsIterationRaises:
    name = "Broken Tools Panel"
    description = "config.tools raises on iteration"
    icon = "x"

    def get_config(self):
        class BadConfig:
            @property
            def tools(self):
                raise RuntimeError("simulated tools iteration failure")

        return BadConfig()


class _PanelCheckPermissionRaises:
    name = "Broken Permission Panel"
    description = "_check_permission always raises"
    icon = "x"

    def get_config(self):
        tool = _make_tool(name="secret_tool")

        class BadConfig:
            tools = [tool]

            def _check_permission(self, user, scope):
                raise RuntimeError("simulated permission check failure")

        return BadConfig()


class _PanelWithoutGetConfig:
    name = "Legacy Panel"
    description = "No get_config — pre-base panels"
    icon = "layers"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetToolsForUser(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.superuser = User.objects.create_user(
            username="superuser",
            password="pass",
            is_staff=True,
            is_superuser=True,
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            password="pass",
            is_staff=True,
            is_superuser=False,
        )
        self.reg = PanelRegistry()
        self.reg._discovered = True

    # --- basic happy path ---

    def test_returns_empty_dict_when_no_panels(self):
        result = self.reg.get_tools_for_user(self.superuser)
        self.assertEqual(result, {})

    def test_panel_without_get_config_exposes_no_tools(self):
        self.reg.register(_PanelWithoutGetConfig, panel_id="legacy")
        result = self.reg.get_tools_for_user(self.superuser)
        self.assertEqual(result, {})

    def test_tools_are_namespaced_by_panel_id(self):
        tool = _make_tool(name="do_thing")
        self.reg.register(_PanelWithTools, panel_id="my_panel")
        self.reg._panels["my_panel"]._config = _make_config(tools=[tool])

        result = self.reg.get_tools_for_user(self.superuser)
        self.assertIn("my_panel__do_thing", result)

    def test_result_maps_key_to_panel_and_tool_tuple(self):
        tool = _make_tool(name="do_thing")
        self.reg.register(_PanelWithTools, panel_id="my_panel")
        self.reg._panels["my_panel"]._config = _make_config(tools=[tool])

        result = self.reg.get_tools_for_user(self.superuser)
        panel, returned_tool = result["my_panel__do_thing"]
        self.assertIs(returned_tool, tool)
        self.assertEqual(panel.name, "Tool Panel")

    def test_multiple_tools_from_same_panel_all_present(self):
        tools = [_make_tool("alpha"), _make_tool("beta"), _make_tool("gamma")]
        self.reg.register(_PanelWithTools, panel_id="panel_a")
        self.reg._panels["panel_a"]._config = _make_config(tools=tools)

        result = self.reg.get_tools_for_user(self.superuser)
        self.assertIn("panel_a__alpha", result)
        self.assertIn("panel_a__beta", result)
        self.assertIn("panel_a__gamma", result)

    def test_tools_from_multiple_panels_all_present(self):
        tool_a = _make_tool("tool_a")
        tool_b = _make_tool("tool_b")

        class PanelA(_PanelWithTools):
            pass

        class PanelB(_PanelWithTools):
            pass

        self.reg.register(PanelA, panel_id="panel_a")
        self.reg.register(PanelB, panel_id="panel_b")
        self.reg._panels["panel_a"]._config = _make_config(tools=[tool_a])
        self.reg._panels["panel_b"]._config = _make_config(tools=[tool_b])

        result = self.reg.get_tools_for_user(self.superuser)
        self.assertIn("panel_a__tool_a", result)
        self.assertIn("panel_b__tool_b", result)

    # --- permission filtering ---

    def test_superuser_required_tool_excluded_for_non_superuser(self):
        tool = _make_tool(name="admin_only")
        self.reg.register(_PanelWithTools, panel_id="restricted")
        self.reg._panels["restricted"]._config = _make_config(
            tools=[tool], require_superuser=True
        )

        result = self.reg.get_tools_for_user(self.staff_user)
        self.assertNotIn("restricted__admin_only", result)

    def test_superuser_required_tool_included_for_superuser(self):
        tool = _make_tool(name="admin_only")
        self.reg.register(_PanelWithTools, panel_id="restricted")
        self.reg._panels["restricted"]._config = _make_config(
            tools=[tool], require_superuser=True
        )

        result = self.reg.get_tools_for_user(self.superuser)
        self.assertIn("restricted__admin_only", result)

    # --- fault isolation ---

    def test_broken_get_config_does_not_prevent_other_panels_tools(self):
        """A panel whose get_config() raises must not block tools from other panels."""
        good_tool = _make_tool(name="good_tool")

        class GoodPanel(_PanelWithTools):
            pass

        self.reg.register(_PanelGetConfigRaises, panel_id="broken")
        self.reg.register(GoodPanel, panel_id="good")
        self.reg._panels["good"]._config = _make_config(tools=[good_tool])

        result = self.reg.get_tools_for_user(self.superuser)

        self.assertIn("good__good_tool", result)
        broken_keys = [k for k in result if k.startswith("broken__")]
        self.assertEqual(broken_keys, [])

    def test_broken_tools_iteration_does_not_prevent_other_panels_tools(self):
        """A panel whose config.tools raises on iteration must not block other panels."""
        good_tool = _make_tool(name="good_tool")

        class GoodPanel(_PanelWithTools):
            pass

        self.reg.register(_PanelToolsIterationRaises, panel_id="broken")
        self.reg.register(GoodPanel, panel_id="good")
        self.reg._panels["good"]._config = _make_config(tools=[good_tool])

        result = self.reg.get_tools_for_user(self.superuser)

        self.assertIn("good__good_tool", result)
        broken_keys = [k for k in result if k.startswith("broken__")]
        self.assertEqual(broken_keys, [])

    def test_broken_check_permission_does_not_prevent_other_panels_tools(self):
        """A panel whose _check_permission() raises must not block other panels."""
        good_tool = _make_tool(name="good_tool")

        class GoodPanel(_PanelWithTools):
            pass

        self.reg.register(_PanelCheckPermissionRaises, panel_id="broken")
        self.reg.register(GoodPanel, panel_id="good")
        self.reg._panels["good"]._config = _make_config(tools=[good_tool])

        result = self.reg.get_tools_for_user(self.superuser)

        self.assertIn("good__good_tool", result)
        broken_keys = [k for k in result if k.startswith("broken__")]
        self.assertEqual(broken_keys, [])

    def test_all_three_failure_modes_together_good_panel_still_works(self):
        """Multiple broken panels in the same registry don't cascade."""
        good_tool = _make_tool(name="survivor")

        class GoodPanel(_PanelWithTools):
            pass

        self.reg.register(_PanelGetConfigRaises, panel_id="broken_config")
        self.reg.register(_PanelToolsIterationRaises, panel_id="broken_tools")
        self.reg.register(_PanelCheckPermissionRaises, panel_id="broken_perms")
        self.reg.register(GoodPanel, panel_id="good")
        self.reg._panels["good"]._config = _make_config(tools=[good_tool])

        result = self.reg.get_tools_for_user(self.superuser)

        self.assertEqual(list(result.keys()), ["good__survivor"])

    def test_broken_panel_warning_is_logged(self):
        """A warning is emitted for each panel that fails, not silently swallowed."""
        self.reg.register(_PanelGetConfigRaises, panel_id="broken")

        with self.assertLogs("dj_control_room.registry", level="WARNING") as cm:
            self.reg.get_tools_for_user(self.superuser)

        self.assertTrue(
            any("broken" in msg for msg in cm.output),
            msg=f"Expected a warning mentioning 'broken', got: {cm.output}",
        )
