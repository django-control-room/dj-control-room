"""
DJ Control Room panel for Local Panel.

Project (unpackaged) panel. Registered with the hub from AppConfig.ready()
via ``registry.register``, not via a setuptools entry point.
"""

from dj_control_room_base.core import PanelPlugin


class DcrLocalPanelPanel(PanelPlugin):
    name = "Local Panel"
    description = "Local Panel Control Room panel"
    icon = "cog"

    app_name = "dcr_local_panel"

    def get_config(self):
        from .conf import panel_config

        return panel_config
