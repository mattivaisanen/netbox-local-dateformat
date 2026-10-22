# Changelog

## Unreleased

New:
- Show dates in NetBox's web UI as `dd.mm.yyyy` instead of ISO 8601:
  lists, detail pages, changelog, journal, date pickers in forms and the
  footer clock. Stored data, CSV exports and the API stay ISO.
- Each user picks their own format on the Preferences page; the default
  for everyone is set under Admin → System → Configuration. Both are saved
  in NetBox's existing settings, with no new tables or migrations.
