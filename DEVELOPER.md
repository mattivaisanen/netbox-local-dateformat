# Developer guide

How the plugin works and why, for anyone changing it.

## Why it patches NetBox

NetBox 4.x has no date format setting. Tables and detail pages don't use
Django's `DATE_FORMAT`; they call NetBox's own ISO helpers:

| NetBox code | Used for |
|---|---|
| `netbox.tables.columns.DateColumn.render` / `DateTimeColumn.render` | Date and date-time columns in object lists |
| `utilities.templatetags.builtins.filters.isodate` / `isodatetime` | The `isodate` / `isodatetime` template filters on detail pages and the changelog |
| `netbox.tables.columns.isodatetime` | Custom field columns (imported by name into `columns`) |

There is no plugin hook for any of these, so `LocalDateFormatConfig.ready()`
replaces them. The template filters are replaced twice: as module
attributes (for Python callers) and in the template library's `filters`
dict (templates look them up there, not on the module).

`render()` is patched but `value()` is not: NetBox uses `value()` for CSV
exports, so exports stay ISO. The REST API and GraphQL don't use any of
these helpers.

Django's own `|date` filter is handled without patching: when
`FORMAT_MODULE_PATH` isn't already set, the plugin points it at
`netbox_local_dateformat/formats/`.

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

`tests/test_dateformat.py` tests the patched helpers directly;
`tests/test_views.py` renders a real NetBox page.

## CI

`.github/workflows/test.yml` checks out NetBox at each tag in the matrix
(oldest supported and latest tested), writes a `configuration.py`, runs
migrations, `collectstatic`, a migration drift check and the test suite.
