from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^save/', views.save_reservation, name='reserve_save'),
    re_path(r'^books/', views.get_books, name='reserve_books'),
    re_path(r'^get/', views.get_reservations, name='reserve_get'),
    re_path(r'^update/(?P<reservation_id>\d+)/', views.update_reservation, name='reserve_update'),
    re_path(r'^delete/', views.delete_reservation, name='reserve_delete'),
]
