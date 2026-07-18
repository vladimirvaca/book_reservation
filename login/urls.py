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
    re_path(r'^admins/$', views.admins, name='admins'),
    re_path(r'^admins/get/', views.get_admins, name='admin_get'),
    re_path(r'^admins/save/', views.save_admin, name='admin_save'),
    re_path(r'^admins/edit/(?P<admin_id>\d+)', views.edit_admin, name='admin_edit'),
    re_path(r'^admins/delete/', views.delete_admin, name='admin_delete'),
    re_path(r'^logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
