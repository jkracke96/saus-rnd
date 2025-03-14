from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired
from django.conf import settings
from django.http import HttpResponseRedirect
from .forms import DocumentForm
from .models import CVDocument
from django.shortcuts import redirect
from django.contrib import messages

import time

VOICE_AGENT_URL = settings.VOICE_AGENT_URL
CV_UPLOAD_FOLDER = settings.CV_UPLOAD_FOLDER

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/main.html', {})

@login_required
def redirect_to_voice_assistant_view(request):
    username = request.user.username
    user_id = request.user.id
    signer = TimestampSigner(settings.SECRET_KEY)
    token = signer.sign(request.user.id)
    time.sleep(0)
    try:
        status = signer.unsign(token, max_age=240)
        print(status)
    except SignatureExpired: 
        print("NO ACCESS")
    return HttpResponseRedirect(f"{VOICE_AGENT_URL}?participantName={username}&id={user_id}&token={token}")


@login_required
def user_uploads_view(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        print("FROM", form.errors)
        if form.is_valid():
            document = form.save(commit=False)  # Don't save to DB yet
            document.user = request.user  # Assign logged-in user
            document.save()  # Now save to DB
            messages.success(request, 'File uploaded successfully')
            return redirect('user_uploads')  # Redirect after successful upload
    # load all user files
    documents_qs = CVDocument.objects.filter(user=request.user)
    return  render(request, 'dashboard/user_uploads.html', {"documents": documents_qs})


@login_required
def delete_user_file_view(request, file_name):
    file_name = file_name[2:len(file_name)-2]
    document = CVDocument.objects.get(file=file_name)
    file_name = document.file.name
    document.delete()
    messages.success(request, f'{file_name} deleted successfully')
    return redirect('user_uploads')
