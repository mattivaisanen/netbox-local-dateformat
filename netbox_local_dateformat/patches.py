"""
Replace NetBox's hard-coded ISO date display with the user's format.

NetBox 4.x has no date format setting and no plugin hook for any of this,
so these functions patch NetBox and Django internals at startup. Each patch
only changes what is rendered for the user; none of them change how a value
is parsed, stored or exported. DEVELOPER.md lists every patched function.
"""
import datetime
import zoneinfo

from django import forms
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.utils import formats as dj_formats
from django.utils.dateformat import format as dj_format
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from .formats import CONFIG_PARAM, DATE_FORMATS, get_date_format, placeholder, timestamp_date_format

# NetBox's footer clock: {% now 'Y-m-d H:i:s T' %} in base/layout.html.
FOOTER_FORMAT = 'Y-m-d H:i:s T'


def apply():
    patch_template_filters()
    patch_table_columns()
    patch_django_formats()
    patch_now_tag()
    patch_date_pickers()
    add_system_default()


def _date(value):
    return dj_format(value, get_date_format())


def _timestamp_date(value):
    """Date part of an aware or naive datetime, shortened (see formats.py)."""
    if value.tzinfo:
        value = localtime(value)
        now = localtime()
    else:
        now = datetime.datetime.now()
    return dj_format(value, timestamp_date_format(value, now))


#
# isodate / isodatetime template filters (detail pages, changelog, journal)
#

def patch_template_filters():
    from netbox.tables import columns
    from utilities.templatetags.builtins import filters

    def isodate(value):
        if type(value) is datetime.date:
            return mark_safe(f'<span title="{naturalday(value)}">{_date(value)}</span>')
        if type(value) is datetime.datetime:
            return mark_safe(f'<span title="{naturaltime(value)}">{_timestamp_date(value)}</span>')
        return ''

    def isodatetime(value, spec='seconds'):
        if type(value) is not datetime.datetime:
            return ''
        text = f'{isodate(value)} {filters.isotime(value, spec=spec)}'
        return mark_safe(f'<span title="{naturaltime(value)}">{text}</span>')

    # Templates look filters up in the library, Python callers on the module.
    for fn in (isodate, isodatetime):
        fn.is_safe = False
        setattr(filters, fn.__name__, fn)
        filters.register.filters[fn.__name__] = fn
    # Custom field columns import isodatetime by name.
    columns.isodatetime = isodatetime


#
# Date and date-time table columns (object lists)
#

def patch_table_columns():
    from netbox.tables import columns

    def date_render(self, value):
        return _date(value) if value else None

    def datetime_render(self, value):
        if not value:
            return None
        value = value.astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
        return f"{_timestamp_date(value)} {value.time().isoformat(timespec=self.timespec)}"

    # render() only: value() is what CSV export uses, and it stays ISO.
    columns.DateColumn.render = date_render
    columns.DateTimeColumn.render = datetime_render


#
# Django's |date filter without an argument (used by some plugins)
#

def patch_django_formats():
    original = getattr(dj_formats.get_format, '_nbldf_original', dj_formats.get_format)
    time_suffix = {
        'DATE_FORMAT': '',
        'SHORT_DATE_FORMAT': '',
        'DATETIME_FORMAT': ' H:i',
        'SHORT_DATETIME_FORMAT': ' H:i',
    }

    def get_format(format_type, lang=None, use_l10n=None):
        # Only display formats; *_INPUT_FORMATS (parsing) are left alone.
        if format_type in time_suffix:
            return get_date_format() + time_suffix[format_type]
        return original(format_type, lang=lang, use_l10n=use_l10n)

    get_format._nbldf_original = original
    dj_formats.get_format = get_format


#
# The footer clock
#

def patch_now_tag():
    from django.template.defaulttags import NowNode

    original = getattr(NowNode.render, '_nbldf_original', NowNode.render)

    def render(self, context):
        if self.format_string == FOOTER_FORMAT:
            now = datetime.datetime.now(datetime.timezone.utc if settings.USE_TZ else None)
            if settings.USE_TZ:
                now = localtime(now)
            text = dj_format(now, f'{get_date_format()} H:i:s T')
            if self.asvar:
                context[self.asvar] = text
                return ''
            return text
        return original(self, context)

    render._nbldf_original = original
    NowNode.render = render


#
# Date pickers in forms
#

def patch_date_pickers():
    """
    NetBox's date pickers are flatpickr inputs that show and submit ISO
    dates. flatpickr reads options from data- attributes, so we ask it for
    an "alt input": the user sees and types their format, while the field
    that is submitted keeps the ISO value. Form parsing is unchanged.
    """
    from utilities.forms.widgets import datetime as widgets

    def picker(widget_class, iso_format, time_part):
        original = getattr(widget_class.get_context, '_nbldf_original', widget_class.get_context)

        def get_context(self, name, value, attrs):
            context = original(self, name, value, attrs)
            fmt = get_date_format()
            context['widget']['attrs'].update({
                'data-alt-input': 'true',
                'data-alt-format': fmt + time_part,
                'data-date-format': iso_format,
                'placeholder': placeholder(fmt) + (' hh:mm:ss' if time_part else ''),
            })
            return context

        get_context._nbldf_original = original
        widget_class.get_context = get_context

    picker(widgets.DatePicker, 'Y-m-d', '')
    picker(widgets.DateTimePicker, 'Y-m-d H:i:S', ' H:i:S')


#
# System default: a field on NetBox's own configuration page
#

def add_system_default():
    """
    Add LOCAL_DATE_FORMAT to NetBox's dynamic configuration parameters, so
    it shows on Admin > System > Configuration and is saved in NetBox's
    existing ConfigRevision data. A NetBox without this plugin ignores the
    extra key, so the database can be moved as is.
    """
    import netbox.config
    from netbox.config.parameters import ConfigParam

    if any(p.name == CONFIG_PARAM for p in netbox.config.PARAMS):
        return
    param = ConfigParam(
        name=CONFIG_PARAM,
        label=_('Default date format'),
        default='',
        description=_(
            'How dates are shown to users who haven\'t picked their own format '
            '(Local Date Format plugin). Stored data stays ISO 8601.'
        ),
        field=forms.ChoiceField,
        field_kwargs={'choices': (('', '---------'), *DATE_FORMATS)},
    )
    params = (*netbox.config.PARAMS, param)

    # Everything that imported PARAMS by name.
    netbox.config.PARAMS = params
    from core import views as core_views
    from core.forms import model_forms
    from utilities.forms.rendering import FieldSet
    core_views.PARAMS = params
    model_forms.PARAMS = params

    form = model_forms.ConfigRevisionForm
    if CONFIG_PARAM not in form.base_fields:
        field = param.field(required=False, label=param.label, help_text=param.description, **param.field_kwargs)
        form.base_fields[CONFIG_PARAM] = field
        form.declared_fields[CONFIG_PARAM] = field
    # Own section, just before the revision comment.
    form.fieldsets = (*form.fieldsets[:-1], FieldSet(CONFIG_PARAM, name=_('Date Format')), form.fieldsets[-1])

    # A config loaded before this ran doesn't know the new default yet.
    netbox.config.clear_config()
