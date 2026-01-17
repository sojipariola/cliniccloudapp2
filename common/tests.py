from django.test import TestCase

from .permissions import has_permission


class PermissionsTest(TestCase):
    def test_has_permission_callable(self):
        # The helper should be importable and callable
        self.assertTrue(callable(has_permission))
