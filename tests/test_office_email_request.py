from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from tenants.models import Tenant
from users.models import CustomUser

class OfficeEmailRequestTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name="Test Clinic", subdomain="test", plan="enterprise")
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            tenant=self.tenant,
            email="user@example.com",
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass123")
        self.url = reverse("office_email_request")

    def test_get_request_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Office Email Setup Request")
        self.assertContains(resp, "Onboarding Instructions")

    def test_post_valid_request_sends_email_and_shows_confirmation(self):
        data = {
            "contact_name": "Dr. Smith",
            "contact_email": "drsmith@example.com",
            "organization": "Test Clinic",
            "domain": "testclinic.com",
            "users": 5,
            "notes": "Please set up 5 mailboxes."
        }
        resp = self.client.post(self.url, data)
        print("RESPONSE CONTENT:\n", resp.content.decode())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Your request has been received")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("Office Email Setup Request", email.subject)
        self.assertIn("Dr. Smith", email.body)
        self.assertIn("testclinic.com", email.body)

    def test_post_invalid_request_shows_errors(self):
        data = {
            "contact_name": "",
            "contact_email": "not-an-email",
            "organization": "",
            "domain": "",
            "users": 0,
            "notes": ""
        }
        resp = self.client.post(self.url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "This field is required", count=3)
        self.assertContains(resp, "Enter a valid email address.")
        self.assertContains(resp, "Ensure this value is greater than or equal to 1.")
