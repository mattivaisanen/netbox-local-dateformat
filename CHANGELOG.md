# Changelog

## Unreleased

New:
- The default date format is set with the plugin's `date_format` setting
  or the `NETBOX_LOCAL_DATE_FORMAT` environment variable.

Removed:
- The "Default date format" field under Admin → System → Configuration.

## 0.1.0 (2026-10-22)

New:
- Show dates in NetBox's web UI as `dd.mm.yyyy` instead of ISO 8601:
  lists, detail pages, changelog, journal, date pickers in forms and the
  footer clock. Stored data, CSV exports and the API stay ISO.
- Each user picks their own format on the Preferences page; the default
  for everyone is set under Admin → System → Configuration. Both are saved
  in NetBox's existing settings, with no new tables or migrations.
- Timestamps from the past week show the weekday, and timestamps from
  earlier this year leave out the year.
