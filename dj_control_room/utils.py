"""
Utility functions for DJ Control Room.
"""

from django.urls import reverse
from django.apps import apps as django_apps
import logging

from .conf import panel_config
from .registry import registry
from .featured_panels import FEATURED_PANELS, get_featured_panel_ids, is_featured_panel

logger = logging.getLogger(__name__)

_VALID_ICON_COLORS = frozenset({
    "accent", "success", "warning", "danger", "info", "muted", "purple", "indigo",
})


def should_register_panel_admin(panel_id=None):
    """
    Check if a panel should register its own admin entry.

    This allows end users to control whether panels show up in both
    DJ Control Room AND their own admin section, or only in DJ Control Room.

    Args:
        panel_id: The panel ID to check (optional, for granular control)

    Returns:
        bool: True if panel should register in admin, False otherwise

    Examples:
        # Simple boolean for all panels
        DJ_CONTROL_ROOM_SETTINGS = {
            'REGISTER_PANELS_IN_ADMIN': True  # Panels show in both places
        }

        # Granular per-panel control
        DJ_CONTROL_ROOM_SETTINGS = {
            'PANEL_ADMIN_REGISTRATION': {
                'redis': True,   # Redis shows in both places
                'cache': False,  # Cache only in Control Room
            }
        }
    """
    panel_specific_configs = panel_config.get_settings("PANEL_ADMIN_REGISTRATION")
    global_panel_config = panel_config.get_settings("REGISTER_PANELS_IN_ADMIN")

    # Per-panel settings take precedence when provided (explicit allow/deny per panel)
    if panel_id and panel_specific_configs:
        panel_admin_visibility = panel_specific_configs.get(
            panel_id, panel_specific_configs.get("*", False)
        )
        return panel_admin_visibility

    # Global setting for all panels
    if global_panel_config:
        return global_panel_config

    # Default: don't register in admin (only show in Control Room)
    return False


def get_panel_config_status(panel_id, panel_app_name):
    """
    Return the configuration status for a panel broken down into its three
    independent conditions:

    - pip_installed     : the package's entry point is registered in the registry
    - in_installed_apps : the Django app is present in INSTALLED_APPS
    - urls_registered   : the panel's URL namespace can be reversed

    ``is_configured`` is True only when all three conditions hold.
    """
    installed_panel = registry.get_panel(panel_id)
    pip_installed = installed_panel is not None

    in_installed_apps = pip_installed and django_apps.is_installed(panel_app_name)

    urls_registered = False
    if pip_installed:
        try:
            url_name = getattr(installed_panel, "get_url_name", lambda: "index")()
            reverse(f"{panel_app_name}:{url_name}")
            urls_registered = True
        except Exception:
            pass

    return {
        "pip_installed": pip_installed,
        "in_installed_apps": in_installed_apps,
        "urls_registered": urls_registered,
        "is_configured": pip_installed and in_installed_apps and urls_registered,
        "installed_panel": installed_panel,
    }


def _normalize_icon_color(color, fallback: str = "muted") -> str:
    """Return color if it's a valid dcr-icon-color variant, otherwise fallback."""
    if color and color in _VALID_ICON_COLORS:
        return color
    return fallback


def get_panel_data(panel):
    """
    Extract data from a registered panel instance.

    Args:
        panel: Panel instance from registry

    Returns:
        dict: Panel data dictionary
    """
    panel_id = panel._registry_id
    featured = is_featured_panel(panel_id)

    # app_name is stamped onto the panel by the registry at discovery time;
    # it defaults to the normalized dist name if not explicitly set.
    panel_app_name = panel.app_name
    config = get_panel_config_status(panel_id, panel_app_name)

    has_install_page = True

    if config["is_configured"]:
        url_name = getattr(panel, "get_url_name", lambda: "index")()
        url = reverse(f"{panel_app_name}:{url_name}")
    elif has_install_page:
        url = reverse("dj_control_room:install_panel", args=[panel_id])
    else:
        url = "#"

    if not config["is_configured"]:
        logger.warning(
            f"Panel '{panel_id}' is registered but its URLs could not be resolved. "
            "Make sure the panel is in INSTALLED_APPS and its URLs are included."
        )

    return {
        "id": panel_id,
        "name": panel.name,
        "description": panel.description,
        "icon": getattr(panel, "icon", "default"),
        "icon_color": _normalize_icon_color(getattr(panel, "icon_color", None)),
        "url": url,
        "installed": True,
        "configured": config["is_configured"],
        "pip_installed": config["pip_installed"],
        "in_installed_apps": config["in_installed_apps"],
        "urls_registered": config["urls_registered"],
        "featured": featured,
        "package": getattr(panel, "package", None),
        "docs_url": getattr(panel, "docs_url", None),
        "pypi_url": getattr(panel, "pypi_url", None),
    }


def get_featured_panels():
    """
    Get featured panels, marking which are installed.

    Returns:
        list: List of featured panel data with installation status
    """
    featured_panels = []

    for featured_meta in FEATURED_PANELS:
        panel_id = featured_meta["id"]

        installed_panel = registry.get_panel(panel_id)

        if installed_panel:
            panel_data = get_panel_data(installed_panel)
            # If the panel object doesn't define icon/icon_color, prefer the
            # curated featured metadata so hub cards stay visually consistent.
            if getattr(installed_panel, "icon", None) in (None, "default"):
                panel_data["icon"] = featured_meta.get("icon", "default")
            if not hasattr(installed_panel, "icon_color"):
                panel_data["icon_color"] = _normalize_icon_color(featured_meta.get("icon_color"))
        else:
            coming_soon = featured_meta.get("coming_soon", False)
            panel_data = {
                "id": panel_id,
                "name": featured_meta["name"],
                "description": featured_meta["description"],
                "icon": featured_meta["icon"],
                "icon_color": _normalize_icon_color(featured_meta.get("icon_color")),
                "url": reverse("dj_control_room:install_panel", args=[panel_id]),
                "status": "coming_soon" if coming_soon else "not_installed",
                "status_label": "COMING SOON" if coming_soon else "NOT INSTALLED",
                "installed": False,
                "configured": False,
                "coming_soon": coming_soon,
                "featured": True,
                "package": featured_meta["package"],
                "docs_url": featured_meta.get("docs_url"),
                "pypi_url": featured_meta.get("pypi_url"),
            }

        featured_panels.append(panel_data)

    return featured_panels


# IDs of first-party infrastructure packages that should not appear as
# community panels on the dashboard. They are presented separately in the
# hub's footer/framework section.
CORE_PANEL_IDS = {"dj_control_room_base"}


def get_community_panels():
    """
    Get community (non-featured, non-core) panels.

    Returns:
        list: List of community panel data
    """
    featured_ids = get_featured_panel_ids()
    excluded_ids = set(featured_ids) | CORE_PANEL_IDS
    community_panels = []

    for panel in registry.get_panels():
        if panel._registry_id not in excluded_ids:
            community_panels.append(get_panel_data(panel))

    return community_panels


def get_core_panel():
    """
    Return display data for the core framework panel (dj-control-room-base),
    or None if it is not installed/registered.

    Returns:
        dict | None: Panel data dictionary, or None
    """
    panel = registry.get_panel("dj_control_room_base")
    if panel is None:
        return None
    return get_panel_data(panel)
