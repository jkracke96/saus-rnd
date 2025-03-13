from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import DocumentForm
from django.shortcuts import redirect
from django.contrib import messages

import time

VOICE_AGENT_URL = settings.VOICE_AGENT_URL

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
    return HttpResponseRedirect(f"{VOICE_AGENT_URL}?participantName={username}&token={token}")


@login_required
def file_upload_view(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        print("FROM", form.errors)
        if form.is_valid():
            document = form.save(commit=False)  # Don't save to DB yet
            document.user = request.user  # Assign logged-in user
            document.save()  # Now save to DB
            messages.success(request, 'File uploaded successfully')
            return redirect('home')  # Redirect after successful upload
    else:
        form = DocumentForm()
        print(form)
    return render(request, 'dashboard/file_upload.html', {'form': form})