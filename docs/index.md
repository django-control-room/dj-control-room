# Django Control Room

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/hero-dark.png">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/hero-light.png">
    <img alt="Django Control Room" src="https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/hero-light.png">
  </picture>
</p>

Django Control Room is a plugin framework for Django admin tools ("panels") and a suite of official panels for Redis, Celery, caches, URLs, Signals, and more. Panels are independent packages built on [dj-control-room-base](https://github.com/django-control-room/dj-control-room-base). The hub discovers them via entry points and renders them in one dashboard with shared CSS, permissions, and admin sidebar integration.

**Official site:** [djangocontrolroom.com](https://djangocontrolroom.com)

![Django Control Room Dashboard](https://raw.githubusercontent.com/django-control-room/dj-control-room/main/images/full-screenshot.png)

---

## Documentation

| Page | What you'll find |
|------|------------------|
| [Installation](installation.md) | Install, `INSTALLED_APPS` (including `dj_control_room_base`), URLs |
| [Configuration](configuration.md) | Settings, sidebar behavior, CSS, MCP |
| [Scopes](scopes.md) | Permission scopes and access control |
| [Theme Adapters](themes.md) | Supported admin skins, screenshots, DIY adapters |
| [Creating Panels](creating-panels.md) | Cookiecutter template and manual panel authoring |
| [API Reference](api-reference.md) | Public API |
| [Contributing](contributing.md) | Local development setup |

### Official panels

- [Redis Panel](https://github.com/django-control-room/dj-redis-panel)
- [Cache Panel](https://github.com/django-control-room/dj-cache-panel)
- [Celery Panel](https://github.com/django-control-room/dj-celery-panel)
- [URLs Panel](https://github.com/django-control-room/dj-urls-panel)
- [Signals Panel](https://github.com/django-control-room/dj-signals-panel)

---

## Quick start

```bash
pip install dj-control-room[all]
```

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "dj_control_room_base",  # required core library
    "dj_redis_panel",
    "dj_cache_panel",
    "dj_urls_panel",
    "dj_control_room",  # list after panels so they appear in one section
]
```

```python
# urls.py
urlpatterns = [
    path("admin/dj-redis-panel/", include("dj_redis_panel.urls")),
    path("admin/dj-cache-panel/", include("dj_cache_panel.urls")),
    path("admin/dj-urls-panel/", include("dj_urls_panel.urls")),
    path("admin/dj-control-room/", include("dj_control_room.urls")),
    path("admin/", admin.site.urls),
]
```

Visit `http://localhost:8000/admin/dj-control-room/`.

See [Installation](installation.md) for the full walkthrough.

---

## Requirements

- Python 3.9+
- Django 4.2+

## Support

- [Official site](https://djangocontrolroom.com)
- [GitHub Discussions](https://github.com/django-control-room/dj-control-room/discussions)
- [Issue tracker](https://github.com/django-control-room/dj-control-room/issues)

## License

MIT. See [LICENSE](https://github.com/django-control-room/dj-control-room/blob/main/LICENSE).

## Credits

Created by [Yasser Toruno](https://github.com/yassi)
