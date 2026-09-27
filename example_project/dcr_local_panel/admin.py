from django.contrib import admin

from dj_control_room_base.core import BasePanelAdmin

from .conf import panel_config
from .models import DcrLocalPanelPlaceholder


@admin.register(DcrLocalPanelPlaceholder)
class DcrLocalPanelPlaceholderAdmin(BasePanelAdmin):
    redirect_url_name = "dcr_local_panel:index"
    panel_config = panel_config
