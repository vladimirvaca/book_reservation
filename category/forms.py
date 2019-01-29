'''
Forms model from category.
'''

from __future__ import unicode_literals
from django import forms

from .models import Category


class CategoryForm(forms.ModelForm):
    category = forms.CharField(required=True)
    description = forms.CharField(required=True)

    class Meta():
        model = Category
        fields = ['category', 'description']
