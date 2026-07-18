'''
Forms for app login
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm


class LoguinForm(forms.Form):
    '''
    Fields of class for the form
    '''
    username = forms.CharField(required=True)
    password = forms.CharField(required=True)


class AdminForm(UserCreationForm):
    '''
    Form for creating new admin users. Inherits username uniqueness,
    password match and AUTH_PASSWORD_VALIDATORS checks from Django.
    '''
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')


class AdminEditForm(forms.ModelForm):
    '''
    Form for editing admin users. Bound to an instance, so username
    uniqueness excludes the admin being edited. Password changes are
    handled separately in the view because they are optional.
    '''
    email = forms.EmailField(required=False)

    class Meta:
        model = UserCreationForm.Meta.model
        fields = ['username', 'email']
