# Configuration reference

The date format a user sees is picked in this order:

1. The user's own **Date format** preference (Preferences → Plugins).
2. `plugins.netbox_local_dateformat.date_format` in NetBox's
   `DEFAULT_USER_PREFERENCES`, if set.
3. **Default date format** under Admin → System → Configuration
   (`LOCAL_DATE_FORMAT`).
4. The `date_format` plugin setting below.
5. `d.m.Y`.

## In the NetBox UI

| Where | Key | Stored in | Choices |
|---|---|---|---|
| Preferences → Plugins → Date format | `plugins.netbox_local_dateformat.date_format` | The user's preferences (`UserConfig`) | System default, `d.m.Y`, `Y-m-d`, `d/m/Y`, `m/d/Y`, `d-m-Y`, `Y/m/d` |
| Admin → System → Configuration → Default date format | `LOCAL_DATE_FORMAT` | The configuration revision (`ConfigRevision`) | empty, `d.m.Y`, `Y-m-d`, `d/m/Y`, `m/d/Y`, `d-m-Y`, `Y/m/d` |

Both are tables NetBox already has; the plugin adds none.

## In `configuration.py`

Under `PLUGINS_CONFIG['netbox_local_dateformat']`:

| Key | Type | Default | Description |
|---|---|---|---|
| `date_format` | `str` | `'d.m.Y'` | Fallback when neither a user preference nor a System default is set. Any Django date format string (see Django's [`date` filter](https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date)). Date pickers in forms pass it to flatpickr, which understands `d`, `m`, `Y`, `j`, `n` and `y` the same way. |

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
