from django.shortcuts import render
from visits.models import PageVisits
from dashboard.views import dashboard_view


def landing_dashboard_page_view(request):
    if request.user.is_authenticated:
        return dashboard_view(request)
    qs = PageVisits.objects.all()
    PageVisits.objects.create(path=request.path)
    return render(request, "landing/main.html", {"page_view_count": qs.count()})


def feature_interviews_view(request):
    return render(request, "features/interview.html")


def feature_cv_generator_view(request):
    return render(request, "features/cv_generator.html")
