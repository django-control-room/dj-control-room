from django.urls import path
from . import views, mcp_views

app_name = "dj_control_room"

urlpatterns = [
    path("", views.index, name="index"),
    path("install/<str:panel_id>/", views.install_panel, name="install_panel"),
    path("mcp/", mcp_views.mcp_endpoint, name="mcp"),
]
