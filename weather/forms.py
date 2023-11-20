from django import forms
from django.forms import ModelForm, TextInput
from .models import city
from django.core.validators import EmailValidator


class CityForm(ModelForm):
    class Meta:
        model = city
        fields = ['name']
        widgets = {
            'name': TextInput(attrs={'class': 'input', 'placeholder': 'Search for a city'})
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name *'}))
    email = forms.CharField(validators=[EmailValidator()], widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Email *'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone Number *'}))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject *'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message *', 'cols': 20, 'rows': 4}))
