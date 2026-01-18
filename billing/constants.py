from decimal import Decimal

TRIAL_DAYS = 14

PLAN_DETAILS = {
    "free_trial": {
        "name": "Free Trial",
        "price": Decimal("0.00"),
        "currency": "USD",
        "interval": None,
        "max_users": 2,
        "max_patients": 5,
        "max_appointments": 50,
        "features": [
            "Basic patient management",
            "Limited appointments",
            "No advanced features",
        ],
    },
    "starter": {
        "name": "Starter",
        "price": Decimal("29.00"),
        "currency": "GBP",
        "interval": "monthly",
        "stripe_price_id": "price_1Sq10xRej9S8svw9YT6MM8k0",
        "max_users": 5,
        "max_patients": 100,
        "max_appointments": 500,
        "features": [
            "Up to 5 users",
            "Up to 100 patients",
            "Appointment scheduling",
            "Lab management",
            "Email support",
        ],
    },
    "professional": {
        "name": "Professional",
        "price": Decimal("99.00"),
        "currency": "GBP",
        "interval": "monthly",
        "stripe_price_id": "price_1Sq14ORej9S8svw9nFi0azAE",
        "max_users": 20,
        "max_patients": 500,
        "max_appointments": 2000,
        "features": [
            "Up to 20 users",
            "Up to 500 patients",
            "Full appointment scheduling",
            "Lab & clinical records",
            "Priority support",
            "AI note-taking",
            "Billing management",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price": Decimal("299.00"),
        "currency": "GBP",
        "interval": "monthly",
        "stripe_price_id": "price_1Sq15jRej9S8svw9FjUS6k9W",
        "max_users": None,  # Unlimited
        "max_patients": None,  # Unlimited
        "max_appointments": None,  # Unlimited
        "features": [
            "Unlimited users",
            "Unlimited patients",
            "All features included",
            "FHIR integration",
            "Custom integrations",
            "Dedicated support",
            "SLA guarantee",
            "Optional Office Email Setup (custom domain)",
        ],
    },
}

# Helper map: Stripe price_id -> internal plan key
PRICE_TO_PLAN = {
    PLAN_DETAILS["starter"]["stripe_price_id"]: "starter",
    PLAN_DETAILS["professional"]["stripe_price_id"]: "professional",
    PLAN_DETAILS["enterprise"]["stripe_price_id"]: "enterprise",
}
