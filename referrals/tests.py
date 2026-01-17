from django.test import TestCase
from django.urls import reverse

from patients.models import Patient

from .models import Clinic, Referral


class ReferralListViewTest(TestCase):
    def setUp(self):
        clinic = Clinic.objects.create(name="Test Clinic", type="General")
        patient = Patient.objects.create(
            first_name="Ref", last_name="Erred", date_of_birth="1995-03-03"
        )
        Referral.objects.create(clinic=clinic, patient=patient, status="pending")

    def test_referral_list_view(self):
        response = self.client.get(reverse("referral_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ref Erred")
