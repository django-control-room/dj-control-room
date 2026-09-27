from django.shortcuts import render

from .conf import panel_config


@panel_config.permission_required("index")
def index(request):
    context = panel_config.get_context(request, title="Local Panel")
    return render(request, "admin/dcr_local_panel/index.html", context)
