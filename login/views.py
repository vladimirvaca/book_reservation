'''
All views from login app.
'''
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

from .forms import LoguinForm


def index(request):
    '''
    View for load index page
    '''
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def signin_user(request):
    '''
    View for validating user
    '''
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoguinForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"status": "1", "type": "info", "message": "User logged."})
            return JsonResponse({"status": "0", "type": "warn",
                                 "message": "Password or user incorrect."})
        return JsonResponse({"status": "-1", "type": "warn", "message": "Verify all inputs."})
    return render(request, 'login.html')


@login_required(login_url='/signin')
def dashboard(request):
    '''
    View for load dashboard page
    '''
    return render(request, 'dashboard.html')
