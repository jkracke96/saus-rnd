from django import forms
from .models import CVDocument


class DocumentForm(forms.ModelForm):
    class Meta:
        model = CVDocument
        fields = ('file',)


class JobPostingForm(forms.Form):
    job_url = forms.URLField()
    


