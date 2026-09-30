from django.urls import reverse

from .base import CeleryPanelTestCase


class TestLocalPanelExample(CeleryPanelTestCase):
    def test_local_panel_appears_under_project_panels(self):
        response = self.client.get(reverse("dj_control_room:index"))

        self.assertEqual(response.status_code, 200)
        project_ids = [panel["id"] for panel in response.context["internal_panels"]]
        community_ids = [panel["id"] for panel in response.context["community_panels"]]
        self.assertIn("dcr_local_panel", project_ids)
        self.assertNotIn("dcr_local_panel", community_ids)
        self.assertContains(response, "Project Panels")
        self.assertContains(response, "Local Panel")

    def test_local_panel_index_is_reachable(self):
        response = self.client.get(reverse("dcr_local_panel:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Local Panel")
