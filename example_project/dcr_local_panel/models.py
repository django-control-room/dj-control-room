from dj_control_room_base.core import PanelPlaceholderModel


class DcrLocalPanelPlaceholder(PanelPlaceholderModel):
    class Meta(PanelPlaceholderModel.Meta):
        verbose_name = "Local Panel"
        verbose_name_plural = "Local Panel"
