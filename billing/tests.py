from django.test import TestCase

from tenants.models import Tenant

from .models import BillingPlan


class BillingPlanModelTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Tenant", subdomain="testtenant")
        BillingPlan.objects.create(name="Basic", price=100, tenant=self.tenant)

    def test_billing_plan_created(self):
        plan = BillingPlan.objects.get(name="Basic")
        self.assertEqual(plan.price, 100)
        self.assertEqual(plan.tenant, self.tenant)
