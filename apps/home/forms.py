from django import forms
from datetime import datetime

from apps.authentication.models import Register
from .models import Category, Comment_Report, Project, Project_Report, Reply, Tag
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
   
    tag = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(),
                                            widget=forms.SelectMultiple(
        attrs={
            "class": "form-control"
        }
    ),required=False)

    class Meta:
        model = Project
        fields = ('title',
                  'details',
                  'total_target',
                  'start_time',
                  'end_time',
                  'category',
                  'tag')
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_time")
        today_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

        if today_date.date() > end_date.date():
            msg = "End date should be greater than Current date [ Should be after today !]."
            self._errors["end_time"] = self.error_class([msg])
        else:
            if end_date <= start_date:
                msg = "End date should be greater than start date."
                self._errors["end_time"] = self.error_class([msg])
   

class Report_form(forms.ModelForm):
    
    class Meta:
        model=Project_Report
        fields=['report']

class Comment_report_form(forms.ModelForm):
    
    class Meta:
        model=Comment_Report
        fields=['report']

class Reply_form(forms.ModelForm):

    class Meta:
        model=Reply
        fields =['reply']

class Category_form(forms.ModelForm):

    class Meta:
        model=Category
        fields=['name']

    # def clean(self):
    #     categories=Category.objects.all()
    #     cleaned_data = super().clean()
    #     name = cleaned_data.get("name")
    #     for category in categories:
    #         if name == category.name:
    #             print('mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')
    #             msg = "not valid clean"
    #             self._errors["name"] = self.error_class([msg])
    #             break
    #         else:
    #             print('qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq')
            
        
          