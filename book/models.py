# -*- coding: utf-8 -*-
'''
Models for book app.
'''
from __future__ import unicode_literals

from django.db import models
from category.models import Category

# Create your models here.


class Book(models.Model):
    '''
    Model of book
    '''
    number_serie = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    category_book = models.ForeignKey(Category)
    resume = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name
