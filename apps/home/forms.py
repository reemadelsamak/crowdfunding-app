from django import forms
from .models import Category, Project, Tag, User
from django.forms.widgets import NumberInput


class Project_Form(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Title",
                "class": "form-control"
            }
        ))
    
    details = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Details",
                "class": "form-control",
                'rows': '3'
            }
        ))
    
    total_target = forms.FloatField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Total Target",
                "class": "form-control",
                "onkeypress":"return (event.charCode !=8 && event.charCode ==0 || (event.charCode >= 48 && event.charCode <= 57))"
            }
        ))

    start_time = forms.DateTimeField(
        widget=NumberInput(
            attrs={
                'placeholder': 'Start date & time',
                'type': 'datetime-local',
                'class': 'form-control'
            }
        ))

    end_time = forms.DateTimeField(
        widget=NumberInput(
            attrs={
                'placeholder': 'End date & time',
                'type': 'datetime-local',
                'class': 'form-control'
            }
        ))

    category = forms.ModelChoiceField(queryset=Category.objects.all(),
                                      widget=forms.Select(
        attrs={
            "class": "form-control"
        }
    ))
    
    user = forms.ModelChoiceField(queryset=User.objects.all(),
                                     widget=forms.Select(
        attrs={
            "class": "form-control"
        }
    ))
   
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                            widget=forms.SelectMultiple(
        attrs={
            "class": "form-control"
        }
    ))

    class Meta:
        model = Project
        fields = ('title',
                  'details',
                  'total_target',
                  'start_time',
                  'end_time',
                  'category',
                  'user',
                  'tag')
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_time")
        if end_date <= start_date:
            msg = "End date should be greater than start date."
            self._errors["end_time"] = self.error_class([msg])

