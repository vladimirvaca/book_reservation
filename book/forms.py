'''
Forms model from book.
'''

from __future__ import unicode_literals
from django import forms

from .models import Book
from category.models import Category


class BookForm(forms.ModelForm):
    number_serie = forms.CharField(required=True)
    name = forms.CharField(required=True)
    category_book = forms.ModelChoiceField(queryset=Category.objects.all())
    resume = forms.CharField(required=True)

    class Meta():
        model = Book
        fields = ['number_serie', 'name', 'category_book', 'resume']
