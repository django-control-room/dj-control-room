"""
Tests for the dynamic admin integration layer.

Key behaviours covered:
- Framework panels (those in FRAMEWORK_PANEL_IDS) are never registered in admin
- Regular panels are registered as expected
- FRAMEWORK_PANEL_IDS is hub-controlled and cannot be bypassed by panel authors
"""

from unittest.mock import MagicMock, patch

from django.contrib import admin
from django.test import TestCase

from dj_control_room.admin_integration import _register_panel_admin
from dj_control_room.featured_panels import FRAMEWORK_PANEL_IDS


def _make_panel(registry_id, app_name=None):
    """Return a minimal mock panel stamped with _registry_id and app_name."""
    panel = MagicMock()
    panel._registry_id = registry_id
    panel.app_name = app_name or registry_id
    panel.name = f"Panel {registry_id}"
    panel.get_url_name.return_value = "index"
    panel.get_config.return_value = None
    return panel


class TestFrameworkPanelIds(TestCase):
    def test_dj_control_room_base_is_a_framework_panel(self):
        """dj_control_room_base must always be in FRAMEWORK_PANEL_IDS."""
        self.assertIn("dj_control_room_base", FRAMEWORK_PANEL_IDS)

    def test_framework_panel_ids_is_a_frozenset(self):
        """FRAMEWORK_PANEL_IDS must be immutable so panel authors cannot mutate it."""
        self.assertIsInstance(FRAMEWORK_PANEL_IDS, frozenset)


class TestRegisterPanelAdminFrameworkSkip(TestCase):
    def test_framework_panel_is_not_registered_in_admin(self):
        """_register_panel_admin must skip panels in FRAMEWORK_PANEL_IDS."""
        panel = _make_panel("dj_control_room_base")
        before = set(admin.site._registry.keys())

        _register_panel_admin(panel)

        after = set(admin.site._registry.keys())
        self.assertEqual(
            before, after, "No new model should be registered for a framework panel"
        )

    def test_regular_panel_is_registered_in_admin(self):
        """_register_panel_admin must register models for non-framework panels."""
        panel = _make_panel("dj_test_panel_unique_xyz")
        before = set(admin.site._registry.keys())

        _register_panel_admin(panel)

        added = set(admin.site._registry.keys()) - before
        self.addCleanup(lambda: [admin.site.unregister(m) for m in added])
        self.assertGreater(len(added), 0, "A regular panel should add an admin model")

    def test_all_framework_panel_ids_are_skipped(self):
        """Every ID in FRAMEWORK_PANEL_IDS is skipped, not just dj_control_room_base."""
        for fwk_id in FRAMEWORK_PANEL_IDS:
            with self.subTest(framework_id=fwk_id):
                panel = _make_panel(fwk_id)
                before = set(admin.site._registry.keys())
                _register_panel_admin(panel)
                after = set(admin.site._registry.keys())
                self.assertEqual(before, after)
