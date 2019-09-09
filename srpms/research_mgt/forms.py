from django import forms
from .models import Course


class ContractForm(forms.Form):
    course_number = forms.ModelChoiceField(required=True, queryset=Course.objects.values_list('course_number', flat=True).distinct(), empty_label="(Nothing)")
    title = forms.CharField(required=True, max_length=100)
    year = forms.IntegerField(required=True)
    semester = forms.CharField(required=True, max_length=20)
    duration = forms.IntegerField(required=True)
    object = forms.CharField(required=True, max_length=200)
    description = forms.CharField(required=True, max_length=500)
