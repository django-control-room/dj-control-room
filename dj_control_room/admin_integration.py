"""
Dynamic admin integration for DJ Control Room panels.

Automatically registers admin entries for all discovered panels,
grouped under the "DJ Control Room" app in the admin sidebar.
"""

import logging

from django.contrib import admin
from django.db import models

from dj_control_room_base.core import BasePanelAdmin

from .registry import registry
from .utils import should_register_panel_admin
from .featured_panels import get_featured_panel_ids, FRAMEWORK_PANEL_IDS

logger = logging.getLogger(__name__)


def unregister_panel_placeholders():
    """
    Unregister panel placeholder models from the admin so they only appear
    under "DJ Control Room" (via our proxy models).

    Call this from admin.py when dj_control_room is listed after panel apps
    in INSTALLED_APPS, so all panel admin modules have already been imported.
    Skips panels where the user has opted in to show in both places
    (REGISTER_PANELS_IN_ADMIN or PANEL_ADMIN_REGISTRATION).
    """
    registry.autodiscover()
    to_unregister = []
    for model, _ in list(admin.site._registry.items()):
        try:
            if not getattr(model._meta, "managed", True) and model._meta.app_label:
                panel_id = model._meta.app_label
                if registry.is_registered(panel_id) and not should_register_panel_admin(
                    panel_id
                ):
                    to_unregister.append(model)
        except Exception:
            continue
    for model in to_unregister:
        try:
            admin.site.unregister(model)
            logger.debug(f"Unregistered panel placeholder: {model._meta.label}")
        except Exception as e:
            logger.warning(f"Could not unregister {model._meta.label}: {e}")


def register_panel_admins():
    """
    Dynamically register admin entries for all discovered panels.

    Creates a proxy model and admin class for each panel, allowing them
    to appear in the Django admin sidebar under "DJ Control Room".

    Each panel entry redirects to the panel's URL when clicked.
    """
    # Discover all panels first
    registry.autodiscover()

    for panel in registry.get_panels():
        try:
            _register_panel_admin(panel)
        except Exception as e:
            logger.error(
                f"Failed to register admin for panel '{panel._registry_id}': {e}",
                exc_info=True,
            )


def _register_panel_admin(panel):
    """
    Register a single panel in the admin.

    Framework panels (those listed in FRAMEWORK_PANEL_IDS) are skipped because
    their URL namespaces are not required to be mounted by the consuming project,
    and they have no end-user view to navigate to from the sidebar.

    Args:
        panel: The panel instance to register
    """
    if panel._registry_id in FRAMEWORK_PANEL_IDS:
        logger.debug(
            f"Skipping admin registration for framework panel '{panel._registry_id}'"
        )
        return

    # Create a safe model name from the registry ID
    model_name = (
        f"{panel._registry_id.replace('-', '').replace('_', '').title()}PanelProxy"
    )

    # Check if already registered
    try:
        existing_model = admin.site._registry
        for model in existing_model.keys():
            if model.__name__ == model_name:
                logger.debug(
                    f"Panel proxy model {model_name} already registered, skipping"
                )
                return
    except Exception:
        pass

    # Community panels are prefixed with "[+] " so they always sort
    # after featured panels in the sidebar. "[" (ASCII 91) is greater than all
    # uppercase letters (max "Z" = 90), which is what Django uses to sort
    # models within an app in get_app_list.
    is_featured = panel._registry_id in get_featured_panel_ids()
    display_name = panel.name if is_featured else f"[+] {panel.name}"

    # Create the proxy model class dynamically
    model_attrs = {
        "__module__": "dj_control_room.models",
        "Meta": type(
            "Meta",
            (),
            {
                "managed": False,  # Don't create database table
                "verbose_name": display_name,
                "verbose_name_plural": display_name,
                "app_label": "dj_control_room",  # Key: groups under DJ Control Room
            },
        ),
    }

    model_class = type(model_name, (models.Model,), model_attrs)

    # Get the URL name from the panel (default to "index" if method missing)
    url_name = getattr(panel, "get_url_name", lambda: "index")()
    panel_id = panel.app_name

    # panel_config is None for older panels that don't inherit from PanelPlugin
    # or haven't implemented get_config(). BasePanelAdmin falls back to is_staff.
    panel_config = getattr(panel, "get_config", lambda: None)()

    admin_class_name = f"{model_name}Admin"
    admin_class = type(admin_class_name, (BasePanelAdmin,), {
        "redirect_url_name": f"{panel_id}:{url_name}",
        "panel_config": panel_config,
    })

    # Register it with the admin site
    admin.site.register(model_class, admin_class)

    logger.debug(
        f"Registered admin entry for panel '{panel._registry_id}' ({panel.name})"
    )
