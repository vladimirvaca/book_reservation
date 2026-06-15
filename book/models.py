'''
Models for book app.
'''
from django.db import models

from category.models import Category


class Book(models.Model):
    '''
    Model of book
    '''
    number_serie = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    category_book = models.ForeignKey(Category, on_delete=models.CASCADE)
    resume = models.CharField(max_length=100)

    def __str__(self):
        return self.name
