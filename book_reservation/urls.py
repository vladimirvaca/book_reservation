"""book_reservation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import re_path, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, re_path


def healthz(_request):
    """
    Anonymous health probe used by the Docker HEALTHCHECK and the deploy
    pipeline to verify the expected version is live.
    """
    return JsonResponse({'status': 'ok', 'version': settings.APP_VERSION})


urlpatterns = [
    re_path(r'^healthz$', healthz, name='healthz'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^', include('login.urls')),
    re_path(r'^book/', include('book.urls')),
    re_path(r'^category/', include('category.urls')),
    re_path(r'^reserve/', include('reserve.urls')),
]
