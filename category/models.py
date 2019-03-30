# -*- coding: utf-8 -*-
'''
Models of category
'''

from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Category(models.Model):
    '''
    Model category
    '''
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __unicode__(self):
        return self.category
