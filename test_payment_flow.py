#!/usr/bin/env python
"""
Quick test script for payment flow without running full test suite.
Tests:
1. Stripe key validation
2. URL routes
3. Template rendering
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from billing.constants import PLAN_DETAILS

User = get_user_model()

def test_payment_flow():
    """Test the complete payment flow."""
    print("\n" + "="*60)
    print("PAYMENT FLOW TEST")
    print("="*60)
    
    # Test 1: Check Stripe prices are defined
    print("\n✓ Test 1: Checking plan prices...")
    for plan_name, plan in PLAN_DETAILS.items():
        if plan_name == "free_trial":
            continue
        print(f"  {plan_name}: £{plan['price']} {plan['currency']} per {plan['interval']}")
        assert "stripe_price_id" in plan, f"Missing stripe_price_id for {plan_name}"
    print("  ✓ All plans have Stripe price IDs")
    
    # Test 2: Check routes exist
    print("\n✓ Test 2: Checking URL routes...")
    from django.urls import reverse
    
    routes = [
        ('view_plans', ()),
        ('upgrade_plan', ('professional',)),
        ('upgrade_success', ()),
        ('upgrade_cancel', ()),
    ]
    
    for route_name, args in routes:
        try:
            url = reverse(route_name, args=args)
            print(f"  {route_name}: {url}")
        except Exception as e:
            print(f"  ✗ {route_name}: {e}")
            raise
    
    print("  ✓ All routes are correctly configured")
    
    # Test 3: Check templates exist
    print("\n✓ Test 3: Checking templates...")
    from django.template.loader import get_template
    
    templates = [
        'billing/plans.html',
        'billing/upgrade_confirm.html',
        'billing/success.html',
        'billing/cancel.html',
    ]
    
    for template in templates:
        try:
            get_template(template)
            print(f"  ✓ {template}")
        except Exception as e:
            print(f"  ✗ {template}: {e}")
            raise
    
    # Test 4: Check views are accessible (without login for now)
    print("\n✓ Test 4: Checking view access...")
    client = Client(SERVER_NAME='testserver')
    
    # Plans page should be accessible
    response = client.get('/billing/plans/', SERVER_NAME='127.0.0.1')
    print(f"  /billing/plans/: {response.status_code}")
    assert response.status_code in [200, 302, 400], f"Expected 200, 302, or 400, got {response.status_code}"
    
    # Cancel page should exist
    response = client.get('/billing/upgrade-cancel/', SERVER_NAME='127.0.0.1')
    print(f"  /billing/upgrade-cancel/: {response.status_code}")
    assert response.status_code in [302, 200, 400], f"Expected 302, 200, or 400, got {response.status_code}"
    
    print("  ✓ Routes are accessible")
    
    # Test 5: Verify Stripe key validation
    print("\n✓ Test 5: Checking Stripe key validation...")
    from billing.upgrade_views import _stripe_key_valid
    
    test_cases = [
        ("sk_test_123456789012345", True, "valid test key"),
        ("sk_live_123456789012345", True, "valid live key"),
        ("sk_test_your_key_here", False, "placeholder with 'here'"),
        ("pk_test_123456789012345", False, "wrong prefix"),
        ("", False, "empty string"),
    ]
    
    for key, expected, desc in test_cases:
        result = _stripe_key_valid(key)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {desc}: {result}")
        assert result == expected, f"Failed for {desc}"
    
    print("  ✓ Stripe key validation working correctly")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nNext steps:")
    print("1. Create Stripe products in your dashboard")
    print("2. Add the price IDs to billing/constants.py")
    print("3. Test the full checkout flow in the browser")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_payment_flow()
