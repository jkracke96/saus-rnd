from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired
from django.conf import settings
from django.http import HttpResponseRedirect

import time

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/main.html', {})

@login_required
def redirect_to_voice_assistant_view(request):
    username = request.user.username
    signer = TimestampSigner(settings.SECRET_KEY)
    token = signer.sign(request.user.id)
    time.sleep(0)
    try:
        status = signer.unsign(token, max_age=240)
        print(status)
    except SignatureExpired: 
        print("NO ACCESS")
    return HttpResponseRedirect(f"http://localhost:3000/?participantName={username}&token={token}")