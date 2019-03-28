# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Book
from category.models import Category
from .forms import BookForm

# Create your views here.


@login_required(login_url='/signin')
def book(request):
    return render(request, 'book.html')


@login_required(login_url='/signin')
def get_books(request):
    if request.method == 'GET':
        books_raw = list(Book.objects.raw(
            "SELECT * FROM book_book"))
        books = [{"id": r.id, "number_serie": r.number_serie,
                  "name": r.name, "category": Category.objects.get(pk=r.category_book_id).category, "resume": r.resume} for r in books_raw]
        return JsonResponse({"data": books}, safe=False)


@login_required(login_url='/signin')
def save_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "Book category."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})


@login_required(login_url='/signin')
def edit_book(request, id):
    book = Book.objects.get(pk=id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "Book edited."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})


@login_required(login_url='/signin')
def delete_book(request):
    if request.method == 'POST':
        id_book = request.POST['delete_book_id']
        book = Book.objects.get(pk=id_book)
        book.delete()
        return JsonResponse({"status": "1", "type": "success", "message": "Book deleted."})
