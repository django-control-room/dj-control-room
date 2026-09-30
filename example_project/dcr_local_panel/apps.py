from django.apps import AppConfig


class DcrLocalPanelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dcr_local_panel"
    verbose_name = "Local Panel"

    def ready(self):
        """Register this unpackaged panel with the Control Room hub.

        Unpackaged apps have no entry point. List this app before
        ``dj_control_room`` in INSTALLED_APPS so the hub sidebar picks it up.
        """
        try:
            from dj_control_room.registry import registry
        except ImportError:
            return
        from .panel import DcrLocalPanelPanel

        registry.register(
            DcrLocalPanelPanel,
            panel_id="dcr_local_panel",
        )
