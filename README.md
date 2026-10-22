# NetBox Local Date Format

A small NetBox plugin that shows dates in the web UI in each user's own
format, for example `22.10.2026 14:55` instead of ISO 8601
(`2026-10-22 14:55`).

Only the display changes. Stored data, CSV exports and the REST/GraphQL
API stay ISO 8601, and the plugin adds no database tables or migrations,
so the database can be moved to a NetBox without this plugin as is.

## Choosing the format

- **Each user:** *Preferences* (user menu) → *Plugins* → **Date format**.
  "System default" follows the default below.
- **Default for everyone:** the `date_format` setting in the plugin's
  `PLUGINS_CONFIG` block, or the `NETBOX_LOCAL_DATE_FORMAT` environment
  variable. Without either, `d.m.Y`.

Choices: `31.12.2026`, `2026-12-31`, `31/12/2026`, `12/31/2026`,
`31-12-2026`, `2026/12/31`. Times stay `HH:MM:SS`.

Timestamps (a date and a time, like "created" or changelog times) are
shortened: within the past week they show the weekday (`Thu 14:55:07`),
earlier this year they leave out the year (`15.10. 14:55:07`). Hover for
the relative time. Plain dates, like a circuit's end date, always show
the full date.

## What changes

- Dates in object lists, detail pages, the changelog and journal
- Date and date-time pickers in forms: you see and type your format, but
  the form still sends an ISO date, so what is saved doesn't change
- The clock in the page footer
- Django's `|date` filter (used by some plugins)

## What stays ISO

- Everything stored in the database
- CSV exports, the REST API and GraphQL

## Where the settings are stored

Each user's choice is saved in their NetBox user preferences
(`plugins.netbox_local_dateformat.date_format`), a table NetBox already
has. The default lives in your configuration or environment, not in the
database. A NetBox without the plugin ignores the saved preference.

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

# Optional default for users who haven't picked a format: any Django
# date format string. Without it, the NETBOX_LOCAL_DATE_FORMAT environment
# variable is used, then "d.m.Y".
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
