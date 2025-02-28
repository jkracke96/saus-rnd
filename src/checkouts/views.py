from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseBadRequest

import helpers.billing

from subscriptions.models import SubscriptionPrice, Subscription, UserSubscription

BASE_URL = settings.BASE_URL
User = get_user_model()

def product_price_redirect_view(request, price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = price_id
    return redirect('stripe-checkout-start')


@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    try:
        obj = SubscriptionPrice.objects.get(id=checkout_subscription_price_id)
    except:
        obj = None
    if not checkout_subscription_price_id or not obj:
        return redirect('pricing')
    customer_stripe_id = request.user.customer.stripe_id
    success_url_path = reverse("stripe-checkout-end")
    pricing_url_path = reverse("pricing")
    success_url = f"{BASE_URL}{success_url_path}"
    cancel_url = f"{BASE_URL}{pricing_url_path}"
    price_stripe_id = obj.stripe_id

    url = helpers.billing.start_checkout_session(
        customer_stripe_id,
        success_url=success_url,
        cancel_url=cancel_url,
        price_stripe_id=price_stripe_id,
        raw=False
    )
    return redirect(url)


def checkout_finalize_view(request):
    session_id = request.GET.get('session_id')
    checkout_data = helpers.billing.get_checkout_customer_plan(session_id)
    plan_id = checkout_data.pop("plan_id")
    customer_id = checkout_data.pop("customer_id")
    sub_stripe_id = checkout_data.pop("sub_stripe_id")
    subscription_data = {**checkout_data}
    try:
        sub_obj = Subscription.objects.get(subscriptionprice__stripe_id=plan_id) # reverse relationship lookup
    except:
        sub_obj = None
    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id) # reverse relationship lookup
    except:
        user_obj = None

    _user_sub_exists = False
    updated_sub_options = {
        "subscription": sub_obj,
        "stripe_id": sub_stripe_id,
        "user_cancelled": False,
        **subscription_data
    }
    try:
        _user_sub_obj = UserSubscription.objects.get(user=user_obj)
        _user_sub_exists = True
    except UserSubscription.DoesNotExist:
        _user_sub_obj = UserSubscription.objects.create(
            user=user_obj,
            **updated_sub_options
        )
    except:
        _user_sub_obj = None
    if None in [sub_obj, user_obj, _user_sub_obj]:
        return HttpResponseBadRequest("There was an Error with your Account. Please contact support.")
    if _user_sub_exists:
        # cancel old subscription
        old_strip_id = _user_sub_obj.stripe_id
        same_stripe_id = old_strip_id == sub_stripe_id
        if old_strip_id and not same_stripe_id:
            helpers.billing.cancel_subscription(
                old_strip_id,
                reason="auto end, new subscription",
                feedback="other",
            )
        # assign new subscription
        for k, v in updated_sub_options.items():
            setattr(_user_sub_obj, k, v)
        _user_sub_obj.save()
        messages.success(request, "Success! Thank you for joining.")
        return redirect(_user_sub_obj.get_absolute_url())
    context = {}
    return render(request, 'checkout/success.html', context)
