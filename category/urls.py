'''
Urls for category app.
'''
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.category, name='category'),
    re_path(r'^save/', views.save_category, name='category_save'),
    re_path(r'^get/', views.get_categories, name='category_get'),
    re_path(r'^search/', views.get_categories_search, name='category_get_search'),
    re_path(r'^edit/(?P<category_id>\d+)', views.edit_category, name='category_edit'),
    re_path(r'^delete/', views.delete_category, name='category_delete'),
]
