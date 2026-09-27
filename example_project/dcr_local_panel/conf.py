from dj_control_room_base.core import PanelConfig

# Read this via panel_config.get_settings(), never django.conf.settings directly.
panel_config = PanelConfig(
    settings_key="DCR_LOCAL_PANEL_SETTINGS",
    defaults={
        "LOAD_DEFAULT_CSS": True,
        "EXTRA_CSS": [],
    },
)
