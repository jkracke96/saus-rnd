import pathlib
from django.shortcuts import render
from django.http import HttpResponse

from visits.models import PageVisits

this_dir = pathlib.Path(__file__).resolve().parent  # get cfehome dir

def home_page_view(request, *args, **kwargs):
    qs = PageVisits.objects.all()
    page_qs = PageVisits.objects.filter(path=request.path)
    my_title = "My Page"
    my_context = {
        "page_title": my_title,
        "page_visit_count": page_qs.count(),
        "total_visit_count": qs.count()
    }
    html_template = "home.html"
    PageVisits.objects.create(path=request.path)
    return render(request, html_template, my_context)


def home_old_page_view(request, *args, **kwargs):
    my_title = "My Page"
    html_ = ""
    html_file_path = this_dir / "home.html"
    html_ = html_file_path.read_text()
    return HttpResponse(html_)