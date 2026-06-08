from django.contrib import admin

from dj_control_room_base.core import BasePanelAdmin

from .admin_integration import unregister_panel_placeholders
from .models import DjControlRoomDashboard


@admin.register(DjControlRoomDashboard)
class DjControlRoomDashboardAdmin(BasePanelAdmin):
    """
    Admin entry for the DJ Control Room dashboard.

    Shows up first in the DJ Control Room section of the admin sidebar.
    Individual panels are registered dynamically via admin_integration.py.
    """

    redirect_url_name = "dj_control_room:index"


# Unregister panel placeholders so they only appear under DJ Control Room.
# Requires dj_control_room to be listed after panel apps in INSTALLED_APPS.
unregister_panel_placeholders()
