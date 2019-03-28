# -*- coding: utf-8 -*-
'''Here are all the necessary views for the characteristics of Category to work.'''
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required

from .forms import CategoryForm
from .models import Category
# Create your views here.


@login_required(login_url='/signin')
def category(request):
    return render(request, 'category.html')


@login_required(login_url='/signin')
def save_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "Saved category."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})


@login_required(login_url='/signin')
def edit_category(request, id):
    category = Category.objects.get(pk=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "Category edited."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})


@login_required(login_url='/signin')
def get_categories(request):
    if request.method == 'GET':
        categories_raw = list(Category.objects.raw(
            "SELECT * FROM category_category"))
        categories = [{"id": r.id, "category": r.category,
                       "description": r.description} for r in categories_raw]
        return JsonResponse({"data": categories}, safe=False)


@login_required(login_url='/signin')
def get_categories_search(request):
    if request.method == 'GET':
        criteria = "'%" + request.GET['criteria'] + "%'"
        categories_raw = list(Category.objects.raw(
            "SELECT * FROM category_category WHERE category_category.category LIKE {0} LIMIT 5".format(criteria)))
        categories = [{"id": r.id, "category": r.category,
                       "description": r.description} for r in categories_raw]
        return JsonResponse(categories, safe=False)


@login_required(login_url='/signin')
def delete_category(request):
    if request.method == 'POST':
        id_category = request.POST['delete_category_id']
        category = Category.objects.get(pk=id_category)
        category.delete()
        return JsonResponse({"status": "1", "type": "success", "message": "Category deleted."})
