"""
Featured panels - curated panels created by DJ Control Room.

These panels are always shown in the dashboard, even if not installed.
If not installed, they show a marketing page with installation instructions.
"""

FEATURED_PANELS = [
    {
        "id": "dj_redis_panel",
        "name": "Redis Panel",
        "description": "Monitor connections, memory, keys, and throughput.",
        "icon": "database",
        "package": "dj-redis-panel",
        "docs_url": "https://github.com/yassi/dj-redis-panel",
        "pypi_url": "https://pypi.org/project/dj-redis-panel/",
        "features": [
            "View connection info and server overview",
            "Search and inspect keys with pattern matching",
            "Monitor memory usage, hit rate, and throughput",
            "Inspect key types, TTL, and serialized values",
        ],
    },
    {
        "id": "dj_cache_panel",
        "name": "Cache Panel",
        "description": "Inspect cached entries, hit/miss ratios.",
        "icon": "layers",
        "package": "dj-cache-panel",
        "docs_url": "https://github.com/yassi/dj-cache-panel",
        "pypi_url": "https://pypi.org/project/dj-cache-panel/",
        "features": [
            "Browse all cached keys and their values",
            "Add, edit, and delete individual keys",
            "Flush the entire cache with one click",
            "Works with any Django cache backend",
        ],
    },
    {
        "id": "dj_celery_panel",
        "name": "Celery Panel",
        "description": "Track workers, monitor task queues.",
        "icon": "chart",
        "package": "dj-celery-panel",
        "docs_url": "https://github.com/yassi/dj-celery-panel",
        "pypi_url": "https://pypi.org/project/dj-celery-panel/",
        "features": [
            "Monitor active workers and their status",
            "Browse queues and pending task counts",
            "Inspect task results, errors, and tracebacks",
            "Retry or revoke tasks from the admin",
        ],
    },
    {
        "id": "dj_urls_panel",
        "name": "URLs Panel",
        "description": "Browse registered URL patterns.",
        "icon": "link",
        "package": "dj-urls-panel",
        "docs_url": "https://github.com/yassi/dj-urls-panel",
        "pypi_url": "https://pypi.org/project/dj-urls-panel/",
        "features": [
            "Browse all registered URL patterns",
            "Filter by namespace, name, or path",
            "Inspect view functions and their modules",
            "Test URLs with different HTTP methods and parameters",
        ],
    },
    {
        "id": "dj_signals_panel",
        "name": "Signals Panel",
        "description": "Monitor signals, debug connections.",
        "icon": "radio",
        "package": "dj-signals-panel",
        "docs_url": "https://github.com/yassi/dj-signals-panel",
        "pypi_url": "https://pypi.org/project/dj-signals-panel/",
        "features": [
            "Browse all registered Django signals",
            "Inspect handlers with source file and line number",
            "Search by signal name or receiver function",
            "View receiver source code",
        ],
    },
    {
        "id": "dj_error_panel",
        "name": "Error Panel",
        "description": "Monitor errors, stack traces, and exceptions.",
        "icon": "link",
        "coming_soon": True,
        "package": "dj-error-panel",
        "docs_url": "https://github.com/yassi/dj-error-panel",
        "pypi_url": "https://pypi.org/project/dj-error-panel/",
        "features": [
            "Capture and browse unhandled exceptions",
            "Full stack traces with source context",
            "Group errors by type and occurrence count",
            "Mark errors as resolved or ignored",
        ],
    },
]


def get_featured_panel_ids():
    """
    Get list of featured panel IDs.

    Returns:
        list: List of panel IDs
    """
    return [panel["id"] for panel in FEATURED_PANELS]


def get_featured_panel_metadata(panel_id):
    """
    Get metadata for a featured panel.

    Args:
        panel_id: The panel ID to look up

    Returns:
        dict: Panel metadata or None if not found
    """
    for panel in FEATURED_PANELS:
        if panel["id"] == panel_id:
            return panel
    return None


def is_featured_panel(panel_id):
    """
    Check if a panel ID is a featured panel.

    Args:
        panel_id: The panel ID to check

    Returns:
        bool: True if featured panel
    """
    return panel_id in get_featured_panel_ids()
