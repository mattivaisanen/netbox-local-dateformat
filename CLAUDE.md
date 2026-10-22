# Working on this repo

NetBox plugin that shows dates in NetBox's web UI as `dd.mm.yyyy`. Follows
the same conventions as mattivaisanen/netbox-change-approval.

## Rules

- **NetBox support:** only claim what CI tests. `min_version` in
  `LocalDateFormatConfig` is the oldest release in the CI matrix; the
  matrix has the oldest supported and the latest tested release. Keep the
  README "Requirements" section in sync.
- **Python:** `requires-python >= 3.10`; CI runs 3.12.
- **Packaging:** setuptools via `pyproject.toml`, no runtime dependencies
  (NetBox provides Django). Keep `version` in `pyproject.toml` and
  `LocalDateFormatConfig.version` the same. Non-`.py` files must be listed
  in package-data. Not on PyPI: installed with
  `pip install git+https://github.com/mattivaisanen/netbox-local-dateformat.git`.
- **Tests:** Django tests in `netbox_local_dateformat/tests/`, run with
  `python manage.py test netbox_local_dateformat` from a NetBox checkout.
  Every behavior change gets a test. Never skip or weaken a test to get CI
  green.
- **Performance:** no database queries at startup or in `ready()`.
- **Docs:** update in the same commit as the change:
  - `README.md`: Requirements, Installation, Upgrading, what changes and
    what stays ISO, License.
  - `DEVELOPER.md`: how it works and why, especially every patched NetBox
    internal.
  - `docs/configuration.md`: every setting (Key / Type / Default /
    Description).
  - `CHANGELOG.md`: `## Unreleased` on top, releases as
    `## X.Y.Z (YYYY-MM-DD)`, with `New:` and `Fixed:` lists written for
    NetBox users.
- **Commits:** subject says what changes for the user, in plain words. Body
  explains the problem, then the fix, in plain language.
- **Testing on a real NetBox:** Matti has their own NetBox at
  `localhost:8000` and tests there themselves. Don't create or delete NetBox
  instances on their machine.
