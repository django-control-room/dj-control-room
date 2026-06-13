from django.apps import AppConfig
from django.core import checks


class DjControlRoomConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dj_control_room"
    verbose_name = " DJ Control Room"

    def ready(self):
        """
        Initialize the panel registry and register admin entries.

        This discovers all panels registered via entry points and
        automatically creates admin sidebar entries for them.

        All panels will appear grouped under "DJ Control Room" in the
        Django admin sidebar.
        """
        from .registry import registry
        from .admin_integration import register_panel_admins

        # First, discover all panels via entry points
        registry.autodiscover()

        # Then, dynamically register admin entries for each discovered panel
        # This creates proxy models with app_label='dj_control_room' so they
        # all appear together in the admin sidebar
        register_panel_admins()

        checks.register(_check_base_installed)


def _check_base_installed(app_configs, **kwargs):
    """
    Verify that dj_control_room_base is in INSTALLED_APPS.

    dj-control-room templates use the ``dcr_icons`` templatetag library,
    which is provided by dj-control-room-base. Django only discovers
    templatetags from apps that are in INSTALLED_APPS, so omitting
    dj_control_room_base causes a TemplateDoesNotExist / tag-library error
    at runtime.
    """
    from django.apps import apps

    errors = []
    if not apps.is_installed("dj_control_room_base"):
        errors.append(
            checks.Error(
                "'dj_control_room_base' is not in INSTALLED_APPS.",
                hint=(
                    "Add 'dj_control_room_base' to INSTALLED_APPS in your settings. "
                    "dj-control-room requires it for its template tag library (dcr_icons) "
                    "and shared design system. "
                    "See: https://yassi.github.io/dj-control-room/installation/"
                ),
                obj="dj_control_room",
                id="dj_control_room.E001",
            )
        )
    return errors
