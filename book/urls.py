'''
Urls from book app
'''
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.book, name='book'),
    re_path(r'^save/', views.save_book, name='book_save'),
    re_path(r'^edit/(?P<book_id>\d+)', views.edit_book, name='book_edit'),
    re_path(r'^get/', views.get_books, name='get_books'),
    re_path(r'^delete/', views.delete_book, name='book_delete'),
]
