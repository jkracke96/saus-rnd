from django.shortcuts import render
from visits.models import PageVisits

def landing_page_view(request):
    qs = PageVisits.objects.all()
    PageVisits.objects.create(path=request.path)
    return render(request, "landing/main.html", {"page_view_count": qs.count()})
