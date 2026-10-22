# NetBox Local Date Format

A tiny NetBox plugin that shows dates in the web UI as `dd.mm.yyyy`
(for example `22.10.2026 14:55`) instead of ISO 8601 (`2026-10-22 14:55`).

## Why a plugin?

NetBox 4.x has no date format setting. Tables, detail pages and the
changelog use built-in ISO date helpers, so Django's `DATE_FORMAT`
settings don't change what you see. This plugin replaces those helpers
at startup.

## What changes

- Dates in object tables (`DateColumn`, `DateTimeColumn`)
- The `isodate` / `isodatetime` template filters used on detail pages
- Django's `|date` filter (English locale formats), used by some plugins

## What stays ISO

- CSV exports and the REST/GraphQL API
- Date picker inputs in forms
- The server clock in the page footer

## Requirements

- NetBox **4.7** or later. Tested with NetBox 4.7.0 and 4.7.3; NetBox
  refuses to load the plugin on older versions.
- No other plugins or Python packages.

## Installation

The plugin isn't on PyPI; install it from GitHub into NetBox's own Python
environment (on a standard install, `source /opt/netbox/venv/bin/activate`
first):

```bash
pip install git+https://github.com/mattivaisanen/netbox-local-dateformat.git
```

Add it to your NetBox configuration:

```python
PLUGINS = ["netbox_local_dateformat"]

# Optional: any Django date format string (default "d.m.Y").
PLUGINS_CONFIG = {
    "netbox_local_dateformat": {"date_format": "d.m.Y"},
}
```

Restart NetBox. The plugin has no database tables, so there are no
migrations and removing it is just a matter of taking it out of `PLUGINS`.

All settings are listed in [docs/configuration.md](docs/configuration.md).

For netbox-docker, install it in a custom image (see the netbox-docker
wiki on using plugins) and list it in `configuration/plugins.py`.

### Upgrading

`--force-reinstall --no-deps` makes pip fetch the latest code even if it
thinks the installed version is current. Then restart NetBox and its
worker:

```bash
pip install --upgrade --force-reinstall --no-deps git+https://github.com/mattivaisanen/netbox-local-dateformat.git
sudo systemctl restart netbox netbox-rq
```

**Admin → System → Plugins** shows the installed version; compare it with
`CHANGELOG.md`.

## License

Apache License 2.0. See [LICENSE](LICENSE).
