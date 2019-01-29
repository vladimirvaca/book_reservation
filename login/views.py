# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import LoguinForm

# Create your views here.


def index(request):
    return render(request, 'index.html')


def signin_user(request):
    if request.method == 'POST':
        form = LoguinForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"status": "1", "type": "info", "message": "User logged."})
            else:
                return JsonResponse({"status": "0", "type": "warn", "message": "Password or user incorrect."})
        else:
            return JsonResponse({"status": "-1", "type": "warn", "message": "Verify all inputs."})
    return render(request, 'login.html')


@login_required(login_url='/signin')
def dashboard(request):
    return render(request, 'dashboard.html')
