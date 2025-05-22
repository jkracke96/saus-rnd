"""
URL configuration for cfehome project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import home_view, about_view, user_only_view, staff_only_view
from auth import views as auth_views
from subscriptions import views as subscriptions_views
from checkouts import views as checkouts_views
from landing import views as landing_views
from dashboard import views as dashboard_views


urlpatterns = [
    path("", landing_views.landing_dashboard_page_view, name="home"),
    path(
        "redirect-to-voice-assistant/<path:job_url>/",
        dashboard_views.redirect_to_voice_assistant_view,
        name="redirect_to_voice_assistant"
    ),
    path("user-uploads/", dashboard_views.user_uploads_view, name="user_uploads"),
    path(
        'delete-user-upload/<path:file_name>/',
        dashboard_views.delete_user_file_view,
        name="delete_user_file"
    ),
    path(
        'download-cv/<path:file_name>/',
        dashboard_views.download_generated_cv_view,
        name="download_cv"
    ),
     path(
        'delete-generated-cv/<path:file_name>/',
        dashboard_views.delete_generated_cv_view,
        name="delete_generated_cv"
    ),
    path("application-generation/", dashboard_views.application_generation_view, name="application_generation"),
    path("about/", about_view),
    path("hello-world/", home_view),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/billing/', subscriptions_views.user_subscription_view, name="user_subscription"),
    path('accounts/billing/cancel/', subscriptions_views.user_subscription_cancel_view, name="user_subscription_cancel"),
    # path('register/', auth_views.register_view),
    path("protected/user-only/", user_only_view),
    path("protected/staff-only/", staff_only_view),
    path('profiles/', include('profiles.urls')),
    path('pricing/', subscriptions_views.subscription_price_view, name="pricing"),
    path('pricing/<str:interval>/', subscriptions_views.subscription_price_view, name="pricing_interval"),
    path(
        'checkout/sub-price/<int:price_id>/',
        checkouts_views.product_price_redirect_view,
        name="sub-price-checkout"
    ),
    path(
        'checkout/start/',
        checkouts_views.checkout_redirect_view,
        name="stripe-checkout-start"
    ),
    path(
        'checkout/success/',
        checkouts_views.checkout_finalize_view,
        name="stripe-checkout-end"
    ),
    # API
    path('api/user/is_authenticated/<str:token>/', auth_views.api_user_is_authenticated),
]
