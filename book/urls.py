from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.book, name='book'),
    url(r'^save/', views.save_book, name='book_save'),
    url(r'^edit/(?P<id>\d+)', views.edit_book, name='book_edit'),
    url(r'^get/', views.get_books, name='get_books'),
    url(r'^delete/', views.delete_book, name='book_delete'),
]
