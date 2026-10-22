# Developer guide

How the plugin works and why, for anyone changing it.

## Rule one: display only

Nothing in this plugin writes dates or changes how they are parsed. Stored
data, CSV exports, the REST API and GraphQL stay ISO 8601, and the plugin
has no models or migrations, so a database can be moved to a NetBox
without the plugin. Keep it that way: a new feature that needs its own
table is a different plugin.

## Which format (`formats.py`)

`get_date_format()` reads the current request from NetBox's
`netbox.context.current_request` and returns, in order: the user's
preference, NetBox's `DEFAULT_USER_PREFERENCES` (via `UserConfig.get`),
the `LOCAL_DATE_FORMAT` system default, the `date_format` plugin setting,
then `d.m.Y`. `user.config` and `get_config()` are cached per request, so
this costs no queries per row.

## Shorter timestamps

`timestamp_date_format()` shortens the date part of a datetime (never a
plain date): `D` (weekday) within the past 7 days, the user's format
without the year (`without_year()`) earlier in the same year, the full
format otherwise. Used by the `isodate`/`isodatetime` filters for
datetimes and by `DateTimeColumn.render`. The hover title still shows
NetBox's relative time.

## Where the settings live

- **User preference:** `PluginConfig.user_preferences` points at
  `preferences.py`. This is NetBox's documented hook; the value is saved in
  the existing `UserConfig.data` JSON.
- **System default:** NetBox has no hook for plugins to add configuration
  parameters, so `patches.add_system_default()` appends a `ConfigParam` to
  NetBox's `PARAMS` tuple and rebinds it where it was imported by name
  (`netbox.config`, `core.forms.model_forms`, `core.views`), then adds the
  field and a "Date Format" fieldset to `ConfigRevisionForm`. The value is
  saved in the existing `ConfigRevision.data` JSON. NetBox only reads
  parameters it knows by name, so the extra key is ignored without the
  plugin. It is not shown on the read-only System page (that template
  lists parameters by hand).

## What is patched (`patches.py`)

NetBox 4.x renders dates with its own ISO helpers and there is no plugin
hook for them:

| Patched | Used for |
|---|---|
| `netbox.tables.columns.DateColumn.render` / `DateTimeColumn.render` | Date columns in object lists. `value()` (CSV export) is not patched. |
| `utilities.templatetags.builtins.filters.isodate` / `isodatetime` (module and template library) | Detail pages, changelog, journal |
| `netbox.tables.columns.isodatetime` | Custom field columns (imported by name) |
| `django.utils.formats.get_format` | `DATE_FORMAT`, `SHORT_DATE_FORMAT`, `DATETIME_FORMAT`, `SHORT_DATETIME_FORMAT` only, i.e. `\|date` without an argument. Input formats are untouched. |
| `django.template.defaulttags.NowNode.render` | Only `{% now 'Y-m-d H:i:s T' %}`, the footer clock |
| `utilities.forms.widgets.DatePicker` / `DateTimePicker` `.get_context` | Adds `data-alt-input`, `data-alt-format` and `data-date-format`. flatpickr reads options from data attributes, shows a second input in the user's format and keeps the submitted field ISO. |

Each patch remembers the original function, so applying twice is safe.

## Keeping it working across NetBox releases

The patched functions are NetBox internals, so a NetBox release can rename
or change them. That is why `min_version` is the oldest release CI tests
and the README only claims tested versions. When adding a new NetBox
release to the CI matrix, compare the new release's versions of the
functions above with the replacements in `__init__.py`.

`ready()` runs no database queries.

## Running tests

From a NetBox checkout with this plugin installed in editable mode
(`pip install -e /path/to/netbox-local-dateformat`) and listed in `PLUGINS`:

```bash
python manage.py test netbox_local_dateformat
```

`tests/test_dateformat.py` tests the patched helpers directly,
`tests/test_views.py` renders a real NetBox page, and
`tests/test_preferences.py` covers the user preference, the System
default and where both are saved.

## CI

`.github/workflows/test.yml` checks out NetBox at each tag in the matrix
(oldest supported and latest tested), writes a `configuration.py`, runs
migrations, `collectstatic`, a migration drift check and the test suite.
