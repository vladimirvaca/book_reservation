'''
Models of category
'''
from django.db import models


class Category(models.Model):
    '''
    Model category
    '''
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.category
