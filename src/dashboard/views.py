from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.signing import TimestampSigner, SignatureExpired
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from .forms import DocumentForm, JobPostingForm
from .models import CVDocument, GeneratedCV
from .functions import get_text_from_url, get_latest_cv, download_blob_to_stream, extract_text_from_pdf_stream, generate_custom_cv, convert_html_string_to_pdf_io, upload_pdf_io_to_azure
from django.shortcuts import redirect
from django.contrib import messages
import time

VOICE_AGENT_URL = settings.VOICE_AGENT_URL
CV_UPLOAD_FOLDER = settings.CV_UPLOAD_FOLDER
AZURE_GENERATED_CV_CONTAINER=settings.AZURE_GENERATED_CV_CONTAINER

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/main.html', {})

@login_required
def redirect_to_voice_assistant_view(request, job_url):
    if not job_url:
        job_url = ""
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
    return HttpResponseRedirect(f"{VOICE_AGENT_URL}?participantName={username}&id={user_id}&token={token}&job_url={job_url}")


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
    if document.user != request.user:
        messages.error(request, "You do not have permission to delete this file.")
        return redirect('user_uploads')
    file_name = document.file.name
    document.delete()
    messages.success(request, f'{file_name} deleted successfully')
    return redirect('user_uploads')


@login_required
def application_generation_view(request):
    if request.method == 'POST':
        # read from post request for unput email
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_url = form.cleaned_data['job_url']
            job_text = get_text_from_url(job_url)
            job_title = job_text['title']
            job_description = job_text['text']
            user = request.user
            user_id = user.id
            latest_cv_name = get_latest_cv(user_id, CVDocument)
            stream = download_blob_to_stream(latest_cv_name)
            cv_text = extract_text_from_pdf_stream(stream)
            cv_html = generate_custom_cv(cv_text, job_description)
            pdf_io = convert_html_string_to_pdf_io(cv_html)
            blob_obj = upload_pdf_io_to_azure(pdf_io, user_id)
            pdf_url = blob_obj.get("pdf_url")
            pdf_name = blob_obj.get("blob_name")
            generated_cv = GeneratedCV.objects.create(
                user_id=user_id,
                file=pdf_url,
                job_url=job_url,
                job_title=job_title,
                file_name=pdf_name
            )
            generated_cv.save()
            return redirect('application_generation')
    cvs_qs = GeneratedCV.objects.filter(user=request.user)
    return render(request, 'dashboard/application_generation.html', {"cvs":cvs_qs})


@login_required
def download_generated_cv_view(request, file_name):
    file_name = file_name[2:len(file_name)-2]
    print("FILE NAME", file_name)
    document = GeneratedCV.objects.get(file_name=file_name)
    if document.user != request.user:
        messages.error(request, "You do not have permission to download this file.")
        return redirect('application_generation')
    pdf_stream = download_blob_to_stream(document.file_name, container_name=AZURE_GENERATED_CV_CONTAINER)
    response = HttpResponse(pdf_stream.getvalue(), content_type='application/pdf')
    filename = "your_genrated_cv.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def delete_generated_cv_view(request, file_name):
    file_name = file_name[2:len(file_name)-2]
    print("FILE NAME", file_name)
    document = GeneratedCV.objects.get(file_name=file_name)
    if document.user != request.user:
        messages.error(request, "You do not have permission to delete this file.")
        return redirect('application_generation')
    document.delete()
    messages.success(request, f'{file_name} deleted successfully')
    return redirect('application_generation')
