# Configuration reference

The date format a user sees is picked in this order:

1. The user's own **Date format** preference (Preferences → Plugins).
2. `plugins.netbox_local_dateformat.date_format` in NetBox's
   `DEFAULT_USER_PREFERENCES`, if set.
3. The `date_format` plugin setting below.
4. The `NETBOX_LOCAL_DATE_FORMAT` environment variable.
5. `d.m.Y`.

## In the NetBox UI

| Where | Key | Stored in | Choices |
|---|---|---|---|
| Preferences → Plugins → Date format | `plugins.netbox_local_dateformat.date_format` | The user's preferences (`UserConfig`) | System default, `d.m.Y`, `Y-m-d`, `d/m/Y`, `m/d/Y`, `d-m-Y`, `Y/m/d` |

This is a table NetBox already has; the plugin adds none.

## In `configuration.py` or the environment

Under `PLUGINS_CONFIG['netbox_local_dateformat']`:

| Key | Type | Default | Description |
|---|---|---|---|
| `date_format` | `str` | `None` | Default for users who haven't picked their own format. When unset, the `NETBOX_LOCAL_DATE_FORMAT` environment variable is used, then `d.m.Y`. Any Django date format string (see Django's [`date` filter](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date)). Date pickers in forms pass it to flatpickr, which understands `d`, `m`, `Y`, `j`, `n` and `y` the same way. |

Or set the environment variable for the NetBox and worker processes
(for netbox-docker, in `env/netbox.env`):

```
NETBOX_LOCAL_DATE_FORMAT=d.m.Y
```

Example:

```python
PLUGINS_CONFIG = {
    'netbox_local_dateformat': {
        'date_format': 'd.m.Y',
    },
}
```

## Timestamps

Timestamps (a date and a time) are shortened whatever the format: the
weekday within the past week (`Thu 14:55:07`), no year earlier in the
current year (`15.10. 14:55:07`). Plain dates always use the full format.
There is no setting for this.
