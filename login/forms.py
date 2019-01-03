from django import forms


class LoguinForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
