"""
Internal panel classification.

A panel is internal when it joined via register() (no entry point), is not
featured/core, and does not belong to a third-party installed distribution.
"""

from unittest.mock import patch

from django.urls import reverse

from dj_control_room.registry import registry
from dj_control_room.utils import (
    get_community_panels,
    get_internal_panels,
    is_internal_panel,
)

from .base import CeleryPanelTestCase


class _UnpackagedPanel:
    name = "Project Lookup"
    description = "Unpackaged internal panel"
    icon = "cog"


class _ThirdPartyReadyPanel:
    name = "Ready Registered"
    description = "Packaged panel that used register()"
    icon = "cog"
    app_name = "dj_cache_panel"


class _CustomNamespacePanel:
    name = "Custom Namespace"
    description = "Packaged panel with a custom URL namespace"
    icon = "cog"
    app_name = "custom_url_namespace"
    package = "third-party-dist"


class _ImportPackagePanel:
    name = "Import Package"
    description = "Package identity is a top-level import name"
    icon = "cog"
    app_name = "custom_url_namespace"
    package = "third_party_module"


class TestInternalPanels(CeleryPanelTestCase):
    UNPACKAGED_ID = "dcr_project_lookup"
    THIRD_PARTY_ID = "ready_registered_clone"
    CUSTOM_NAMESPACE_ID = "registered_panel_id"
    IMPORT_PACKAGE_ID = "registered_import_package_id"

    def tearDown(self):
        registry._panels.pop(self.UNPACKAGED_ID, None)
        registry._panels.pop(self.THIRD_PARTY_ID, None)
        registry._panels.pop(self.CUSTOM_NAMESPACE_ID, None)
        registry._panels.pop(self.IMPORT_PACKAGE_ID, None)
        super().tearDown()

    def test_register_without_a_distribution_is_internal(self):
        registry.register(_UnpackagedPanel, panel_id=self.UNPACKAGED_ID)

        internal_ids = [panel["id"] for panel in get_internal_panels()]
        community_ids = [panel["id"] for panel in get_community_panels()]

        self.assertIn(self.UNPACKAGED_ID, internal_ids)
        self.assertNotIn(self.UNPACKAGED_ID, community_ids)

        response = self.client.get(reverse("dj_control_room:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Internal Panels")
        self.assertContains(response, "Project Lookup")

    def test_register_from_a_third_party_distribution_is_community(self):
        registry.register(_ThirdPartyReadyPanel, panel_id=self.THIRD_PARTY_ID)

        internal_ids = [panel["id"] for panel in get_internal_panels()]
        community_ids = [panel["id"] for panel in get_community_panels()]

        self.assertNotIn(self.THIRD_PARTY_ID, internal_ids)
        self.assertIn(self.THIRD_PARTY_ID, community_ids)

    def test_distribution_identity_takes_precedence_over_custom_app_name(self):
        registry.register(_CustomNamespacePanel, panel_id=self.CUSTOM_NAMESPACE_ID)
        distributions = {
            "example_project": ["project-dist"],
            "third_party_module": ["third-party-dist"],
        }

        with patch(
            "dj_control_room.utils._packages_distributions",
            return_value=distributions,
        ):
            panel = registry.get_panel(self.CUSTOM_NAMESPACE_ID)
            self.assertFalse(is_internal_panel(panel))

            internal_ids = [panel["id"] for panel in get_internal_panels()]
            community_ids = [panel["id"] for panel in get_community_panels()]

        self.assertNotIn(self.CUSTOM_NAMESPACE_ID, internal_ids)
        self.assertIn(self.CUSTOM_NAMESPACE_ID, community_ids)

    def test_package_import_name_is_used_before_custom_app_name(self):
        registry.register(_ImportPackagePanel, panel_id=self.IMPORT_PACKAGE_ID)
        distributions = {
            "example_project": ["project-dist"],
            "third_party_module": ["third-party-dist"],
        }

        with patch(
            "dj_control_room.utils._packages_distributions",
            return_value=distributions,
        ):
            panel = registry.get_panel(self.IMPORT_PACKAGE_ID)
            self.assertFalse(is_internal_panel(panel))

    def test_entry_point_panels_are_not_internal(self):
        internal_ids = [panel["id"] for panel in get_internal_panels()]
        self.assertNotIn("dj_cache_panel", internal_ids)

    def test_install_page_redirects_internal_panels_to_the_dashboard(self):
        registry.register(_UnpackagedPanel, panel_id=self.UNPACKAGED_ID)

        response = self.client.get(
            reverse("dj_control_room:install_panel", args=[self.UNPACKAGED_ID])
        )
        self.assertRedirects(response, reverse("dj_control_room:index"))
