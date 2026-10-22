from django.test import TestCase, override_settings

import datetime

from circuits.models import Circuit, CircuitType, Provider
from users.models import User


@override_settings(TIME_ZONE='UTC', LOGIN_REQUIRED=True)
class PageTests(TestCase):
    """Dates on real NetBox pages use the plugin's format."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('admin', 'admin@example.com', 'x')
        provider = Provider.objects.create(name='Provider 1', slug='provider-1')
        circuit_type = CircuitType.objects.create(name='Type 1', slug='type-1')
        cls.circuit = Circuit.objects.create(
            cid='C1', provider=provider, type=circuit_type, termination_date=datetime.date(2026, 10, 22),
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.today = datetime.date(2026, 10, 22)  # the circuit's end date

    def test_circuit_detail_page(self):
        response = self.client.get(self.circuit.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.today.strftime('%d.%m.%Y'))
        # Shown as text nowhere (the Clone link's URL keeps it ISO).
        self.assertNotContains(response, f'>{self.today.isoformat()}<')
