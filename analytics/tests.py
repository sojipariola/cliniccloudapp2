from django.test import TestCase

from tenants.models import Tenant

from .models import AnalyticsEvent


class AnalyticsEventModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Tenant", subdomain="testtenant")
        AnalyticsEvent.objects.create(event_type="login", user_id=1, tenant=self.tenant)

    def test_analytics_event_created(self):
        event = AnalyticsEvent.objects.get(event_type="login")
        self.assertEqual(event.event_type, "login")
        self.assertEqual(event.tenant, self.tenant)
