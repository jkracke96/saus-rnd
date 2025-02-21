import stripe
from decouple import config

DJANGO_DEBUG = config('DJANGO_DEBUG', cast=bool, default=False)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default="", cast=str)

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Stripe secret key is invalid for PROD")

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(
        name="",
        email="",
        metadata={},
        raw=False):
    response = stripe.Customer.create(
        name=name,
        email=email,
        metadata=metadata
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id

def create_product(
        name="",
        metadata={},
        raw=False):
    response = stripe.Product.create(
        name=name,
        metadata=metadata
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id

def create_price(
        currency="eur",
        unit_amount=9999,
        interval="month",
        product=None,
        metadata={},
        raw=False):
    if product is None:
        raise ValueError("Product is required")
    response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        recurring={"interval": interval},
        product=product,
        metadata=metadata
    )
    stripe_id = response.id
    return stripe_id