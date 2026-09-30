from django.urls import path

from . import views

app_name = "dcr_local_panel"

urlpatterns = [
    path("", views.index, name="index"),
]
