from django import forms
from .models import Course


class ContractForm(forms.Form):
    course_number = forms.ModelChoiceField(required=True, queryset=Course.objects, empty_label="(Nothing)")
    semester = forms.CharField(required=True, max_length=20)
    student_id = forms.CharField(required=True, max_length=10)
    student_name = forms.CharField(required=True, max_length=100)
    title = forms.CharField(required=True, max_length=100)
    report = forms.IntegerField(required=True)
    artefact = forms.IntegerField(required=True)
    supervisor = forms.CharField(required=True, max_length=100)
    examinor = forms.CharField(required=True, max_length=100)
    notes = forms.CharField(required=True, max_length=500)
