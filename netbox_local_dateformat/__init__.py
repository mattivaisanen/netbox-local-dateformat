"""
Show dates in NetBox's web UI as dd.mm.yyyy.

NetBox renders most dates with hard-coded ISO 8601 helpers (the isodate /
isodatetime template filters and the DateColumn / DateTimeColumn table
columns), so Django's DATE_FORMAT settings alone don't change them. This
plugin swaps those helpers for versions that use the plugin's
"date_format" setting (default "d.m.Y"), and points Django's English
locale formats at formats/en/formats.py. Exports (CSV) and the REST API
stay ISO.
"""
import datetime
import zoneinfo

from django.conf import settings
from django.utils.dateformat import format as dj_format
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from netbox.plugins import PluginConfig


def _date_fmt():
    cfg = getattr(settings, 'PLUGINS_CONFIG', {}).get('netbox_local_dateformat', {})
    return cfg.get('date_format') or 'd.m.Y'


class LocalDateFormatConfig(PluginConfig):
    name = 'netbox_local_dateformat'
    verbose_name = 'Local date format'
    description = 'Show dates in the web UI as dd.mm.yyyy.'
    version = '0.1.0'
    base_url = 'local-dateformat'
    min_version = '4.3.0'
    default_settings = {'date_format': 'd.m.Y'}

    def ready(self):
        super().ready()
        from django.utils import formats

        # Django's |date filter: use our locale format module.
        if not getattr(settings, 'FORMAT_MODULE_PATH', None):
            settings.FORMAT_MODULE_PATH = ['netbox_local_dateformat.formats']
            formats.reset_format_cache()

        from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
        from netbox.tables import columns
        from utilities.templatetags.builtins import filters

        def isodate(value):
            if type(value) is datetime.date:
                return mark_safe(f'<span title="{naturalday(value)}">{dj_format(value, _date_fmt())}</span>')
            if type(value) is datetime.datetime:
                local_value = localtime(value) if value.tzinfo else value
                text = dj_format(local_value.date(), _date_fmt())
                return mark_safe(f'<span title="{naturaltime(value)}">{text}</span>')
            return ''

        def isodatetime(value, spec='seconds'):
            if type(value) is not datetime.datetime:
                return ''
            text = f'{isodate(value)} {filters.isotime(value, spec=spec)}'
            return mark_safe(f'<span title="{naturaltime(value)}">{text}</span>')

        # Template filters: replace both the module attributes and the
        # registered filters (templates look them up in the library).
        for fn in (isodate, isodatetime):
            fn.is_safe = False
            setattr(filters, fn.__name__, fn)
            filters.register.filters[fn.__name__] = fn
        columns.isodatetime = isodatetime  # used by some table columns

        def date_render(self, value):
            return dj_format(value, _date_fmt()) if value else None

        def datetime_render(self, value):
            if not value:
                return None
            value = value.astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
            return f"{dj_format(value.date(), _date_fmt())} {value.time().isoformat(timespec=self.timespec)}"

        columns.DateColumn.render = date_render
        columns.DateTimeColumn.render = datetime_render


config = LocalDateFormatConfig
