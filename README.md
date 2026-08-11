[![Tests](https://github.com/django-control-room/dj-control-room/actions/workflows/test.yml/badge.svg)](https://github.com/django-control-room/dj-control-room/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/django-control-room/dj-control-room/branch/main/graph/badge.svg)](https://codecov.io/gh/django-control-room/dj-control-room)
[![PyPI version](https://badge.fury.io/py/dj-control-room.svg)](https://badge.fury.io/py/dj-control-room)
[![Python versions](https://img.shields.io/pypi/pyversions/dj-control-room.svg)](https://pypi.org/project/dj-control-room/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/dj-control-room.svg)](https://pypi.org/project/dj-control-room/)
[![Awesome Django](https://awesome.re/badge.svg)](https://github.com/wsvincent/awesome-django)


<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/hero-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/hero-light.png">
    <img alt="Django Control Room" src="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/hero-light.png">
  </picture>
</p>

<h1 align="center">Django Control Room</h1>
<p align="center">
  <strong>A framework for building Django admin tools and a growing suite of operational panels for your project.</strong>
</p>

---

Django Control Room is a **plugin framework for building Django admin tools** (called "panels"), and a suite of official panels for services like Redis, Celery, and caches, plus Django internals like URLs and Signals. Every panel, official or third-party, is a small independent Python package built on the public plugin API in [dj-control-room-base](https://django-control-room.github.io/dj-control-room-base/).

Install `dj-control-room` and it discovers compatible panels via Python entry points, renders them in a centralized dashboard, and gives them a shared design system, permissions model, and admin sidebar integration.

![Django Control Room Dashboard](https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/full-screenshot.png)

## Features

- **Plugin framework** - build admin tools on [dj-control-room-base](https://django-control-room.github.io/dj-control-room-base/); custom panels behave like the official ones
- **Centralized dashboard** - installed panels are discovered automatically and shown in one place
- **Shared UI** - responsive design and dark mode via a common design system; [theme adapters](https://django-control-room.github.io/dj-control-room/themes/) for popular admin skins
- **Secure** - package verification and staff-gated access
- **Official panels** - pre-built panels for common operational tasks
- **AI agent integration (MCP)** - one MCP endpoint aggregates every installed panel's tools (see [Configuration](https://django-control-room.github.io/dj-control-room/configuration/#ai-agent-integration-mcp))

## Quick start

```bash
# Core only
pip install dj-control-room

# With specific official panels
pip install dj-control-room[redis,cache,urls]

# Or with all official panels
pip install dj-control-room[all]
```

Add `dj_control_room_base` (required core library), your panels, then `dj_control_room` (so they appear under one admin section):

```python
INSTALLED_APPS = [
    # ...
    "dj_control_room_base",
    "dj_redis_panel",
    "dj_cache_panel",
    "dj_urls_panel",
    "dj_control_room",
]
```

```python
urlpatterns = [
    path("admin/dj-redis-panel/", include("dj_redis_panel.urls")),
    path("admin/dj-cache-panel/", include("dj_cache_panel.urls")),
    path("admin/dj-urls-panel/", include("dj_urls_panel.urls")),
    path("admin/dj-control-room/", include("dj_control_room.urls")),
    path("admin/", admin.site.urls),
]
```

```bash
python manage.py migrate
```

Then visit `http://localhost:8000/admin/dj-control-room/`.

For the full walkthrough, settings (sidebar behavior, MCP), and theme adapters, see [Installation](https://django-control-room.github.io/dj-control-room/installation/), [Configuration](https://django-control-room.github.io/dj-control-room/configuration/), and [Theme Adapters](https://django-control-room.github.io/dj-control-room/themes/).

## Official panels

<div align="center">
  <img src="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/grid_image.png" alt="Official Panels" width="800">
</div>

| Panel | Description | Install |
|-------|-------------|---------|
| **Redis Panel** | Monitor connections, inspect keys, view memory usage | `pip install dj-redis-panel` |
| **Cache Panel** | Inspect cache entries, view hit/miss ratios | `pip install dj-cache-panel` |
| **URLs Panel** | Browse URL patterns, test resolvers | `pip install dj-urls-panel` |
| **Celery Panel** | Monitor workers, track task queues | `pip install dj-celery-panel` |
| **Signals Panel** | Inspect Django signals and receivers | `pip install dj-signals-panel` |

## Creating custom panels

```bash
pip install cookiecutter
cookiecutter https://github.com/django-control-room/cookiecutter-dj-control-room-plugin
```

For a full guide, see [Creating Panels](https://django-control-room.github.io/dj-control-room/creating-panels/) or the [build your own panel](https://djangocontrolroom.com/guides/create-django-control-room-panel) walkthrough.

## Documentation

- **Official site:** [djangocontrolroom.com](https://djangocontrolroom.com)
- **Full docs:** [django-control-room.github.io/dj-control-room](https://django-control-room.github.io/dj-control-room/)

| Page | Contents |
|------|----------|
| [Installation](https://django-control-room.github.io/dj-control-room/installation/) | Install, `INSTALLED_APPS`, URLs |
| [Configuration](https://django-control-room.github.io/dj-control-room/configuration/) | Settings, sidebar, CSS, MCP |
| [Scopes](https://django-control-room.github.io/dj-control-room/scopes/) | Permission scopes |
| [Theme Adapters](https://django-control-room.github.io/dj-control-room/themes/) | Supported admin skins and screenshots |
| [Creating Panels](https://django-control-room.github.io/dj-control-room/creating-panels/) | Build custom panels |
| [API Reference](https://django-control-room.github.io/dj-control-room/api-reference/) | Public API |

## Requirements

- Python 3.9+
- Django 4.2+

## Contributing

See the [Contributing Guide](https://django-control-room.github.io/dj-control-room/contributing/).

## License

MIT. See [LICENSE](https://github.com/django-control-room/dj-control-room/blob/main/LICENSE).

## Credits

Created by [Yasser Toruno](https://github.com/yassi)

---

<p align="center">
  <a href="https://djangocontrolroom.com">Official Site</a> ·
  <a href="https://github.com/django-control-room/dj-control-room">GitHub</a> ·
  <a href="https://github.com/django-control-room/dj-control-room/issues">Issues</a>
</p>
