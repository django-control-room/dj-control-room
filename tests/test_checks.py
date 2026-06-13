"""
Tests for Django system checks in dj-control-room.
"""

from unittest.mock import patch

from django.test import TestCase, override_settings

from dj_control_room.apps import _check_base_installed


class TestBaseInstalledCheck(TestCase):
    """Tests for the dj_control_room.E001 system check."""

    def test_no_errors_when_base_is_installed(self):
        """No errors are returned when dj_control_room_base is in INSTALLED_APPS."""
        errors = _check_base_installed(app_configs=None)
        self.assertEqual(errors, [])

    @override_settings(INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "dj_control_room",
    ])
    def test_error_when_base_is_missing(self):
        """E001 is raised when dj_control_room_base is absent from INSTALLED_APPS."""
        errors = _check_base_installed(app_configs=None)
        self.assertEqual(len(errors), 1)
        error = errors[0]
        self.assertEqual(error.id, "dj_control_room.E001")
        self.assertIn("dj_control_room_base", error.msg)
        self.assertIn("INSTALLED_APPS", error.hint)

    def test_error_contains_actionable_hint(self):
        """The E001 hint tells users exactly what to add to INSTALLED_APPS."""
        with patch("django.apps.apps.is_installed", return_value=False):
            errors = _check_base_installed(app_configs=None)

        self.assertEqual(len(errors), 1)
        self.assertIn("dj_control_room_base", errors[0].hint)
        self.assertIn("dcr_icons", errors[0].hint)
