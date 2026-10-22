from django.test import TestCase, override_settings
from django.utils import timezone

from dcim.models import Site
from users.models import User


@override_settings(TIME_ZONE='UTC', LOGIN_REQUIRED=True)
class PageTests(TestCase):
    """Dates on real NetBox pages use the plugin's format."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('admin', 'admin@example.com', 'x')
        cls.site = Site.objects.create(name='Site 1', slug='site-1')

    def setUp(self):
        self.client.force_login(self.user)
        self.today = timezone.now().date()

    def test_site_detail_page(self):
        response = self.client.get(self.site.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.today.strftime('%d.%m.%Y'))
        # The footer clock is the only ISO date left on the page.
        page = response.content.decode().split('id="footer-stamp"')[0]
        self.assertNotIn(self.today.isoformat(), page)
