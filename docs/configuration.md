# Configuration reference

All settings live under `PLUGINS_CONFIG['netbox_local_dateformat']` in your
NetBox `configuration.py`.

| Key | Type | Default | Description |
|---|---|---|---|
| `date_format` | `str` | `'d.m.Y'` | Django date format string used for dates in tables, detail pages and the changelog (see Django's [`date` filter](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date)). Times keep NetBox's own `HH:MM:SS` format. Read on every page load, but a change needs a NetBox restart like any other `configuration.py` change. |

Example:

```python
PLUGINS_CONFIG = {
    'netbox_local_dateformat': {
        'date_format': 'd.m.Y',
    },
}
```

Dates shown by Django's own `|date` filter (used by some plugins) follow
`netbox_local_dateformat/formats/en/formats.py` instead, which is always
`d.m.Y`. If `FORMAT_MODULE_PATH` is already set in your NetBox
configuration, the plugin leaves it alone and those dates follow your own
format module.
