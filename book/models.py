# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from category.models import Category

# Create your models here.


class Book(models.Model):
    number_serie = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    category_book = models.ForeignKey(Category)
    resume = models.CharField(max_length=100)
