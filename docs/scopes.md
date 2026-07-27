# Scopes

Django Control Room splits its own permission checks into **scopes**: named checkpoints passed to `@panel_config.permission_required(scope)`. Every scope inherits the panel-wide `ALLOWED_GROUPS`/`REQUIRE_SUPERUSER` rule by default; a scope only behaves differently once you add an entry for it under `SCOPE_PERMISSIONS` in `DJ_CONTROL_ROOM_SETTINGS`. This is the same `PanelConfig` permission model documented in the [dj-control-room-base Permissions guide](https://django-control-room.github.io/dj-control-room-base/configuration/#permissions) and used identically by every official panel.

## Reference

| Scope | Type | Protects | Default behavior |
|---|---|---|---|
| `dashboard` | View | `index` view: the Control Room dashboard listing featured/community panels | Any staff user |
| `install` | View | `install_panel` view: the per-panel install/configuration guide | Any staff user |

## Example: restrict the dashboard to a specific group

```python
DJ_CONTROL_ROOM_SETTINGS = {
    # Panel-wide default: any staff member can access the hub
    'ALLOWED_GROUPS': [],

    'SCOPE_PERMISSIONS': {
        # Only ops staff may view the dashboard; everyone else falls
        # through to their individual panels' own admin sections.
        'dashboard': {'ALLOWED_GROUPS': ['ops']},
    },
}
```

Any scope not mentioned in `SCOPE_PERMISSIONS` simply falls back to the panel-wide rule, so you only ever need to write down the exceptions.

## Panel tool scopes (MCP)

The hub's [MCP endpoint](configuration.md#ai-agent-integration-mcp) does not define scopes of its own. It aggregates and re-exposes the tools each *installed panel* already registers in its own `tools.py`, and every tool call is checked against that panel's own scope and `SCOPE_PERMISSIONS`, exactly as if it were called from that panel directly. See each panel's own documentation (e.g. [dj-urls-panel Scopes](https://django-control-room.github.io/dj-urls-panel/scopes/), [dj-signals-panel Scopes](https://django-control-room.github.io/dj-signals-panel/scopes/)) for its tool scopes.
