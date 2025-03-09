from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib.auth import get_user_model
from django.contrib import messages

from django.core.signing import TimestampSigner, SignatureExpired
from django.conf import settings
from django.http import HttpResponseRedirect


User = get_user_model()

# Create your views here.
def login_view(request, *args, **kwargs):
    if request.method == "POST":
        username = request.POST.get("username") or None
        password = request.POST.get("password") or None
        if all([username, password]):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("User is authenticated")
                return redirect("/")
    return render(request, "auth/login.html", {})

def register_view(request, *args, **kwargs):
    if request.method == "POST":
        username = request.POST.get("username") or None
        email = request.POST.get("email") or None
        password = request.POST.get("password") or None
        # user_exists = User.objects.filter(username__iexact=username).exists()
        # email_exists = User.objects.filter(email__iexact=email).exists()
        try:
            User.objects.create_user(username=username, email=email, password=password)
        except:
            print("Error")
    return render(request, "auth/register.html", {})


def api_user_is_authenticated(request, token=None, *args, **kwargs):
    print("TOKEN:", token)
    signer = TimestampSigner(settings.SECRET_KEY)
    try:
        status = signer.unsign(token, max_age=240)
        data = {
            "authenticated": True
        }
    except:
        print("Auth failed")
        data = {
            "authenticated": False
        }
    return JsonResponse(data)