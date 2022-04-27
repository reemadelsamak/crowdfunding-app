from django import forms
from .models import Project


class Project_Form(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Title",
                "class": "form-control"
            }
        ))
    details = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Details",
                "class": "form-control"
            }
        ))
    total_target = forms.FloatField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Total Target",
                "class": "form-control"
            }
        ))
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "placeholder": "Start Time",
                "class": "form-control"
            }
        ))
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "placeholder": "End Time",
                "class": "form-control"
            }
        ))
    category = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Category",
                "class": "form-control"
            }
        ))
    user_id = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "User ID",
                "class": "form-control"
            }
        ))

    class Meta:
        model = Project
        fields = ['title',
                  'details',
                  'total_target',
                  'start_time',
                  'end_time',
                  'category',
                  'user_id']
