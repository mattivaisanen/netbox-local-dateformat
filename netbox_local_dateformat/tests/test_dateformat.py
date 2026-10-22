import datetime
import zoneinfo

from django import forms
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings
from django.utils import formats

from netbox.tables import columns
from utilities.forms.widgets import DatePicker, DateTimePicker
from utilities.templatetags.builtins import filters

UTC = zoneinfo.ZoneInfo('UTC')
DATE = datetime.date(2026, 10, 22)
DATETIME = datetime.datetime(2026, 10, 22, 14, 55, 7, tzinfo=UTC)


def render(template, **context):
    return Template(template).render(Context(context))


def custom_format(fmt):
    return override_settings(PLUGINS_CONFIG={'netbox_local_dateformat': {'date_format': fmt}})


@override_settings(TIME_ZONE='UTC')
class TemplateFilterTests(SimpleTestCase):

    def test_isodate_date(self):
        html = render('{% load helpers %}{{ d|isodate }}', d=DATE)
        self.assertIn('>22.10.2026</span>', html)
        self.assertNotIn('2026-10-22', html)

    def test_isodate_datetime(self):
        html = render('{% load helpers %}{{ d|isodate }}', d=DATETIME)
        self.assertIn('>22.10.2026</span>', html)

    def test_isodatetime(self):
        html = render('{% load helpers %}{{ d|isodatetime }}', d=DATETIME)
        self.assertIn('22.10.2026', html)
        self.assertIn('14:55:07', html)
        self.assertNotIn('2026-10-22', html)

    def test_isodatetime_spec(self):
        html = render('{% load helpers %}{{ d|isodatetime:"minutes" }}', d=DATETIME)
        self.assertIn('14:55', html)
        self.assertNotIn('14:55:07', html)

    def test_other_values_render_empty(self):
        self.assertEqual(filters.isodate(None), '')
        self.assertEqual(filters.isodate('2026-10-22'), '')
        self.assertEqual(filters.isodatetime(DATE), '')

    def test_custom_format(self):
        with custom_format('Y/m/d'):
            html = render('{% load helpers %}{{ d|isodate }}', d=DATE)
        self.assertIn('>2026/10/22</span>', html)

    def test_custom_field_column_uses_patched_filter(self):
        # NetBox's custom field column calls columns.isodatetime by name.
        self.assertIs(columns.isodatetime, filters.isodatetime)


@override_settings(TIME_ZONE='UTC')
class TableColumnTests(SimpleTestCase):

    def test_date_column(self):
        self.assertEqual(columns.DateColumn().render(DATE), '22.10.2026')

    def test_datetime_column(self):
        self.assertEqual(columns.DateTimeColumn().render(DATETIME), '22.10.2026 14:55:07')

    def test_datetime_column_timespec(self):
        self.assertEqual(columns.DateTimeColumn(timespec='minutes').render(DATETIME), '22.10.2026 14:55')

    @override_settings(TIME_ZONE='Europe/Helsinki')
    def test_datetime_column_uses_time_zone(self):
        self.assertEqual(columns.DateTimeColumn().render(DATETIME), '22.10.2026 17:55:07')

    def test_empty_values(self):
        self.assertIsNone(columns.DateColumn().render(None))
        self.assertIsNone(columns.DateTimeColumn().render(None))

    def test_custom_format(self):
        with custom_format('Y/m/d'):
            self.assertEqual(columns.DateColumn().render(DATE), '2026/10/22')

    def test_exports_stay_iso(self):
        # CSV export uses value(), which the plugin leaves alone.
        self.assertEqual(columns.DateColumn().value(DATE), '2026-10-22')
        self.assertEqual(columns.DateTimeColumn().value(DATETIME), '2026-10-22T14:55:07+00:00')


class DjangoDateFilterTests(SimpleTestCase):

    def test_date_filter(self):
        self.assertEqual(render('{{ d|date }}', d=DATE), '22.10.2026')
        self.assertEqual(formats.get_format('SHORT_DATE_FORMAT'), 'd.m.Y')

    def test_input_formats_unchanged(self):
        # Parsing submitted dates must not depend on the display format.
        self.assertIn('%Y-%m-%d', formats.get_format('DATE_INPUT_FORMATS'))

    def test_custom_format(self):
        with custom_format('Y/m/d'):
            self.assertEqual(render('{{ d|date }}', d=DATE), '2026/10/22')

    def test_explicit_format_argument_wins(self):
        self.assertEqual(render('{{ d|date:"Y-m-d" }}', d=DATE), '2026-10-22')


@override_settings(TIME_ZONE='UTC')
class NowTagTests(SimpleTestCase):

    def test_footer_clock(self):
        text = render("{% now 'Y-m-d H:i:s T' %}")
        self.assertRegex(text, r'^\d\d\.\d\d\.\d{4} \d\d:\d\d:\d\d UTC$')

    def test_other_formats_unchanged(self):
        self.assertRegex(render("{% now 'Y-m-d' %}"), r'^\d{4}-\d\d-\d\d$')


class DatePickerTests(SimpleTestCase):

    def test_date_picker(self):
        html = DatePicker().render('d', DATE)
        self.assertIn('value="2026-10-22"', html)  # submitted value stays ISO
        self.assertIn('data-alt-input="true"', html)
        self.assertIn('data-alt-format="d.m.Y"', html)
        self.assertIn('data-date-format="Y-m-d"', html)
        self.assertIn('placeholder="DD.MM.YYYY"', html)

    def test_datetime_picker(self):
        html = DateTimePicker().render('d', '2026-10-22 14:55:07')
        self.assertIn('data-alt-format="d.m.Y H:i:S"', html)
        self.assertIn('data-date-format="Y-m-d H:i:S"', html)

    def test_custom_format(self):
        with custom_format('m/d/Y'):
            html = DatePicker().render('d', DATE)
        self.assertIn('data-alt-format="m/d/Y"', html)
        self.assertIn('placeholder="MM/DD/YYYY"', html)

    def test_form_still_parses_iso(self):
        class Form(forms.Form):
            d = forms.DateField(widget=DatePicker())

        form = Form(data={'d': '2026-10-22'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['d'], DATE)
