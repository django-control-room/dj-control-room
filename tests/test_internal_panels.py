"""
Internal panel classification.

A panel is internal when it joined via register() with no entry point and is
not featured/core. An entry point always makes it community.
"""

from types import SimpleNamespace

from django.urls import reverse

from dj_control_room.featured_panels import get_featured_panel_ids
from dj_control_room.registry import registry
from dj_control_room.utils import (
    get_community_panels,
    get_internal_panels,
    is_internal_panel,
)

from .base import CeleryPanelTestCase


class _ProjectPanel:
    name = "Project Lookup"
    description = "Unpackaged internal panel"
    icon = "cog"


class TestInternalPanels(CeleryPanelTestCase):
    PANEL_ID = "dcr_project_lookup"

    def tearDown(self):
        registry._panels.pop(self.PANEL_ID, None)
        super().tearDown()

    def _section_ids(self):
        internal_ids = [panel["id"] for panel in get_internal_panels()]
        community_ids = [panel["id"] for panel in get_community_panels()]
        return internal_ids, community_ids

    def test_register_without_an_entry_point_is_internal(self):
        registry.register(_ProjectPanel, panel_id=self.PANEL_ID)

        internal_ids, community_ids = self._section_ids()
        self.assertIn(self.PANEL_ID, internal_ids)
        self.assertNotIn(self.PANEL_ID, community_ids)

        response = self.client.get(reverse("dj_control_room:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Internal Panels")
        self.assertContains(response, "Project Lookup")

    def test_entry_point_claiming_a_registered_panel_makes_it_community(self):
        registry.register(_ProjectPanel, panel_id=self.PANEL_ID)
        entry_point = SimpleNamespace(
            name=self.PANEL_ID,
            value="tests.test_internal_panels:_ProjectPanel",
            dist=SimpleNamespace(name=self.PANEL_ID),
            load=lambda: _ProjectPanel,
        )

        registry._load_panel(entry_point)

        internal_ids, community_ids = self._section_ids()
        self.assertNotIn(self.PANEL_ID, internal_ids)
        self.assertIn(self.PANEL_ID, community_ids)

    def test_internal_false_forces_a_registered_panel_into_community(self):
        registry.register(_ProjectPanel, panel_id=self.PANEL_ID, internal=False)

        internal_ids, community_ids = self._section_ids()
        self.assertNotIn(self.PANEL_ID, internal_ids)
        self.assertIn(self.PANEL_ID, community_ids)

    def test_internal_true_keeps_a_panel_internal_even_with_an_entry_point(self):
        registry.register(_ProjectPanel, panel_id=self.PANEL_ID, internal=True)
        entry_point = SimpleNamespace(
            name=self.PANEL_ID,
            value="tests.test_internal_panels:_ProjectPanel",
            dist=SimpleNamespace(name=self.PANEL_ID),
            load=lambda: _ProjectPanel,
        )
        registry._load_panel(entry_point)

        internal_ids, community_ids = self._section_ids()
        self.assertIn(self.PANEL_ID, internal_ids)
        self.assertNotIn(self.PANEL_ID, community_ids)

    def test_internal_override_cannot_move_a_featured_panel(self):
        featured_panel = SimpleNamespace(
            _registry_id=get_featured_panel_ids()[0],
            _from_entry_point=False,
            _internal_override=True,
        )

        self.assertFalse(is_internal_panel(featured_panel))

    def test_entry_point_panels_are_not_internal(self):
        internal_ids = [panel["id"] for panel in get_internal_panels()]
        self.assertNotIn("dj_cache_panel", internal_ids)

    def test_install_page_redirects_internal_panels_to_the_dashboard(self):
        registry.register(_ProjectPanel, panel_id=self.PANEL_ID)

        response = self.client.get(
            reverse("dj_control_room:install_panel", args=[self.PANEL_ID])
        )
        self.assertRedirects(response, reverse("dj_control_room:index"))
