"""
Which date format the current user sees.

The format is looked up in this order:

1. The user's own preference (Preferences page, stored in NetBox's existing
   UserConfig data under plugins.netbox_local_dateformat.date_format).
2. NetBox's DEFAULT_USER_PREFERENCES, if it sets that same key (UserConfig.get
   does this for us).
3. The date_format setting in the plugin's PLUGINS_CONFIG block.
4. The NETBOX_LOCAL_DATE_FORMAT environment variable.
5. d.m.Y.

Only what the user sees changes. Nothing here writes to the database.
"""
import os

from django.conf import settings

from netbox.context import current_request

PLUGIN_NAME = 'netbox_local_dateformat'
PREFERENCE = f'plugins.{PLUGIN_NAME}.date_format'
ENV_VAR = 'NETBOX_LOCAL_DATE_FORMAT'
FALLBACK = 'd.m.Y'

# Django date format strings. Their d, m and Y tokens mean the same thing in
# flatpickr, which NetBox's date pickers use, so forms can use them as is.
DATE_FORMATS = (
    ('d.m.Y', '31.12.2026 (d.m.Y)'),
    ('Y-m-d', '2026-12-31 (Y-m-d, ISO 8601)'),
    ('d/m/Y', '31/12/2026 (d/m/Y)'),
    ('m/d/Y', '12/31/2026 (m/d/Y)'),
    ('d-m-Y', '31-12-2026 (d-m-Y)'),
    ('Y/m/d', '2026/12/31 (Y/m/d)'),
)


def user_format(request=None):
    """The current user's own choice, or '' when they haven't picked one."""
    request = request or current_request.get()
    user = getattr(request, 'user', None)
    if user is None or not user.is_authenticated:
        return ''
    try:
        return user.config.get(PREFERENCE) or ''
    except Exception:
        # No UserConfig row (e.g. a user created outside NetBox's signals).
        return ''


def system_format():
    """The default for users who haven't picked a format."""
    plugin_config = getattr(settings, 'PLUGINS_CONFIG', {}).get(PLUGIN_NAME, {})
    return plugin_config.get('date_format') or os.environ.get(ENV_VAR) or FALLBACK


def get_date_format(request=None):
    return user_format(request) or system_format()


def placeholder(fmt):
    """'d.m.Y' -> 'DD.MM.YYYY', for empty form fields."""
    return fmt.replace('d', 'DD').replace('m', 'MM').replace('Y', 'YYYY')


# Formats without the year, for timestamps from the current year.
_WITHOUT_YEAR = {
    'd.m.Y': 'd.m.',
    'Y-m-d': 'm-d',
    'd/m/Y': 'd/m',
    'm/d/Y': 'm/d',
    'd-m-Y': 'd-m',
    'Y/m/d': 'm/d',
}


def without_year(fmt):
    if fmt in _WITHOUT_YEAR:
        return _WITHOUT_YEAR[fmt]
    # A custom format: drop the year and the separator next to it.
    short = fmt.replace('Y', '').replace('y', '')
    return short.strip(' -/') or fmt


def timestamp_date_format(value, now):
    """
    The date part of a timestamp (a date and time), shortened:

    - within the past week: the weekday, e.g. "Mon"
    - earlier this year: no year, e.g. "22.10."
    - otherwise the full format, e.g. "22.10.2025"

    value and now must be in the same time zone. Plain dates (a circuit's
    end date, for example) always use the full format.
    """
    fmt = get_date_format()
    days_ago = (now.date() - value.date()).days
    if 0 <= days_ago < 7:
        return 'D'
    if value.year == now.year:
        return without_year(fmt)
    return fmt
