import json
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from tenants.models import Tenant
from unittest.mock import patch

class StripeWebhookTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Clinic", subdomain="test")
        self.client = Client()
        self.url = reverse("stripe_webhook")
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET or "whsec_test_secret_12345678901234567890"

    @patch("stripe.Webhook.construct_event")
    def test_checkout_session_completed(self, mock_construct_event):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"plan": "starter", "tenant_id": str(self.tenant.id)},
                    "subscription": "sub_123",
                    "customer": "cus_123",
                }
            },
        }
        mock_construct_event.return_value = event
        response = self.client.post(
            self.url,
            data=json.dumps({}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="testsignature",
        )
        self.assertEqual(response.status_code, 200)
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.plan, "starter")
        self.assertEqual(self.tenant.stripe_subscription_id, "sub_123")
        self.assertEqual(self.tenant.stripe_customer_id, "cus_123")

    def test_invalid_webhook_secret(self):
        with patch("stripe.Webhook.construct_event") as mock_construct_event:
            settings.STRIPE_WEBHOOK_SECRET = "invalid"
            response = self.client.post(
                self.url,
                data=json.dumps({}),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="testsignature",
            )
            self.assertEqual(response.status_code, 400)
            mock_construct_event.assert_not_called()
