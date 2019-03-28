from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.category, name='category'),
    url(r'^save/', views.save_category, name='category_save'),
    url(r'^get/', views.get_categories, name='category_get'),
    url(r'^search/', views.get_categories_search, name='category_get_search'),
    url(r'^edit/(?P<id>\d+)', views.edit_category, name='category_edit'),
    url(r'^delete/', views.delete_category, name='category_delete'),
]
