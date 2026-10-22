import os
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

import datetime

from circuits.models import Circuit, CircuitType, Provider
from netbox.config import clear_config
from users.models import User

PREF = 'plugins.netbox_local_dateformat.date_format'


@override_settings(TIME_ZONE='UTC', LOGIN_REQUIRED=True)
class FormatChoiceTests(TestCase):
    """Each user's own choice, the System default, and the fallback."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('admin', 'admin@example.com', 'x')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Type 1', slug='type-1')
        cls.circuit = Circuit.objects.create(
            cid='C1', provider=provider, type=circuit_type, termination_date=datetime.date(2026, 10, 22),
        )

    def setUp(self):
        cache.delete('config')
        cache.delete('config_version')
        clear_config()
        self.client.force_login(self.user)
        self.today = datetime.date(2026, 10, 22)  # the circuit's end date

    def tearDown(self):
        cache.delete('config')
        cache.delete('config_version')
        clear_config()

    def set_system_default(self, fmt):
        patcher = override_settings(PLUGINS_CONFIG={'netbox_local_dateformat': {'date_format': fmt}})
        patcher.enable()
        self.addCleanup(patcher.disable)

    def set_user_format(self, fmt):
        self.user.config.set(PREF, fmt, commit=True)

    def page(self):
        response = self.client.get(self.circuit.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        return response

    def test_fallback(self):
        self.assertContains(self.page(), self.today.strftime('%d.%m.%Y'))

    def test_system_default(self):
        self.set_system_default('d/m/Y')
        self.assertContains(self.page(), self.today.strftime('%d/%m/%Y'))

    def test_user_choice_wins_over_system_default(self):
        self.set_system_default('d/m/Y')
        self.set_user_format('Y/m/d')
        self.assertContains(self.page(), self.today.strftime('%Y/%m/%d'))

    def test_environment_variable(self):
        with mock.patch.dict(os.environ, {'NETBOX_LOCAL_DATE_FORMAT': 'Y/m/d'}):
            self.assertContains(self.page(), self.today.strftime('%Y/%m/%d'))

    def test_plugin_setting_wins_over_environment_variable(self):
        self.set_system_default('d/m/Y')
        with mock.patch.dict(os.environ, {'NETBOX_LOCAL_DATE_FORMAT': 'Y/m/d'}):
            self.assertContains(self.page(), self.today.strftime('%d/%m/%Y'))

    def test_user_system_default_choice(self):
        self.set_system_default('m/d/Y')
        self.set_user_format('')
        self.assertContains(self.page(), self.today.strftime('%m/%d/%Y'))

    def test_users_see_their_own_format(self):
        other = User.objects.create_user('other', 'other@example.com', 'x', is_superuser=True)
        other.config.set(PREF, 'Y/m/d', commit=True)
        self.assertContains(self.page(), self.today.strftime('%d.%m.%Y'))
        self.client.force_login(other)
        self.assertContains(self.page(), self.today.strftime('%Y/%m/%d'))


@override_settings(LOGIN_REQUIRED=True)
class SettingsPageTests(TestCase):
    """The settings are saved in NetBox's existing storage, not new tables."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('admin', 'admin@example.com', 'x')

    def setUp(self):
        self.client.force_login(self.user)

    def tearDown(self):
        cache.delete('config')
        cache.delete('config_version')
        clear_config()

    def test_preferences_page(self):
        url = reverse('account:preferences')
        response = self.client.get(url)
        self.assertContains(response, PREF)
        response = self.client.post(url, {PREF: 'm/d/Y'})
        self.assertEqual(response.status_code, 302)
        self.user.config.refresh_from_db()
        self.assertEqual(self.user.config.data['plugins']['netbox_local_dateformat']['date_format'], 'm/d/Y')
