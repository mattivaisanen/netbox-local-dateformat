# Changelog

## Unreleased

Fixed:

- NetBox 4.8 and later refuse to load the plugin until it has been tested
  with them, instead of quietly showing ISO dates again after an upgrade.

## 0.1.0 (2026-11-21)

New:

- Show dates in NetBox's web UI as `dd.mm.yyyy` instead of ISO 8601:
  lists, detail pages, changelog, journal, date pickers in forms and the
  footer clock. Stored data, CSV exports and the API stay ISO.
- Each user picks their own format on the Preferences page; the default
  for everyone is set under Admin → System → Configuration. Both are saved
  in NetBox's existing settings, with no new tables or migrations.
- Timestamps from the past week show the weekday, and timestamps from
  earlier this year leave out the year.
