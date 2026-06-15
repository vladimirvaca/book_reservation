'''
Urls for app login
'''
from django.contrib.auth.views import LogoutView
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^dashboard/', views.dashboard, name='dashboard'),
    re_path(r'^signin/', views.signin_user, name='signin'),
    re_path(r'^logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
