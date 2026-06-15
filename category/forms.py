'''
Forms model from category.
'''
from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    '''
    Fields configuration for form
    '''
    category = forms.CharField(required=True)
    description = forms.CharField(required=True)

    class Meta:
        model = Category
        fields = ['category', 'description']
