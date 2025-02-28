import helpers.billing
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from subscriptions.models import SubscriptionPrice, UserSubscription
from subscriptions import utils as subs_utils


@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        finished = subs_utils.refresh_active_users_subscriptions([request.user.id], active_only=False)
        if finished:
            messages.success(request, "Your subscription details have been refreshed.")
        else:
            messages.success(request, "Your subscription details have not been refreshed. Please try again or contact us")
        return redirect(user_sub_obj.get_absolute_url())
    return render(request, "subscriptions/user_detail_view.html", {"subscription": user_sub_obj})


@login_required
def user_subscription_cancel_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == "POST":
        if user_sub_obj.stripe_id and user_sub_obj.is_active_status:
            sub_data = helpers.billing.cancel_subscription(
                user_sub_obj.stripe_id,
                reason="User wanted to end",
                cancel_at_period_end=True,
                feedback="other",
                raw=False
            )
            for k, v in sub_data.items():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Your subscription has been cancelled")
        return redirect(user_sub_obj.get_absolute_url())
    return render(request, "subscriptions/user_cancel_view.html", {"subscription": user_sub_obj})


def subscription_price_view(request, interval="month"):
    inv_mo = SubscriptionPrice.IntervalChoices.MONTHLY
    inv_yr = SubscriptionPrice.IntervalChoices.YEARLY
    qs = SubscriptionPrice.objects.filter(featured=True)
    object_list = qs.filter(interval=inv_mo)
    url_path_name = "pricing_interval"
    mo_url = reverse(url_path_name, kwargs={"interval": inv_mo})
    yr_url = reverse(url_path_name, kwargs={"interval": inv_yr})
    active = inv_mo
    if interval == inv_yr:
        active = inv_yr
        object_list = qs.filter(interval=inv_yr)
    return render(request, "subscriptions/pricing.html", {
        "object_list": object_list,
        "mo_url": mo_url,
        "yr_url": yr_url,
        "active": active,
    })
