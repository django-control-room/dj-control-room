"""
Internal panel classification.

A panel is internal when it joined via register() (no entry point), is not
featured/core, and does not belong to a third-party installed distribution.
"""

from django.urls import reverse

from dj_control_room.registry import registry
from dj_control_room.utils import get_community_panels, get_internal_panels

from .base import CeleryPanelTestCase


class _UnpackagedPanel:
    name = "Project Lookup"
    description = "Unpackaged project panel"
    icon = "cog"


class _ThirdPartyReadyPanel:
    name = "Ready Registered"
    description = "Packaged panel that used register()"
    icon = "cog"
    app_name = "dj_cache_panel"


class TestInternalPanels(CeleryPanelTestCase):
    UNPACKAGED_ID = "dcr_project_lookup"
    THIRD_PARTY_ID = "ready_registered_clone"

    def tearDown(self):
        registry._panels.pop(self.UNPACKAGED_ID, None)
        registry._panels.pop(self.THIRD_PARTY_ID, None)
        super().tearDown()

    def test_register_without_a_distribution_is_internal(self):
        registry.register(_UnpackagedPanel, panel_id=self.UNPACKAGED_ID)

        internal_ids = [panel["id"] for panel in get_internal_panels()]
        community_ids = [panel["id"] for panel in get_community_panels()]

        self.assertIn(self.UNPACKAGED_ID, internal_ids)
        self.assertNotIn(self.UNPACKAGED_ID, community_ids)

        response = self.client.get(reverse("dj_control_room:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Project Panels")
        self.assertContains(response, "Project Lookup")

    def test_register_from_a_third_party_distribution_is_community(self):
        registry.register(_ThirdPartyReadyPanel, panel_id=self.THIRD_PARTY_ID)

        internal_ids = [panel["id"] for panel in get_internal_panels()]
        community_ids = [panel["id"] for panel in get_community_panels()]

        self.assertNotIn(self.THIRD_PARTY_ID, internal_ids)
        self.assertIn(self.THIRD_PARTY_ID, community_ids)

    def test_entry_point_panels_are_not_internal(self):
        internal_ids = [panel["id"] for panel in get_internal_panels()]
        self.assertNotIn("dj_cache_panel", internal_ids)

    def test_install_page_redirects_internal_panels_to_the_dashboard(self):
        registry.register(_UnpackagedPanel, panel_id=self.UNPACKAGED_ID)

        response = self.client.get(
            reverse("dj_control_room:install_panel", args=[self.UNPACKAGED_ID])
        )
        self.assertRedirects(response, reverse("dj_control_room:index"))
