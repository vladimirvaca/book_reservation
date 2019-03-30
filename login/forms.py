'''
Forms for app login
'''
from django import forms


class LoguinForm(forms.Form):
    '''
    Fields of class for the form
    '''
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)
