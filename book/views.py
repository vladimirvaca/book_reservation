# -*- coding: utf-8 -*-
'''
Views for book app
'''
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from category.models import Category
from .models import Book
from .forms import BookForm

# Create your views here.


@login_required(login_url='/signin')
def book(request):
    '''
    Render principal page from book
    '''
    return render(request, 'book.html')


@login_required(login_url='/signin')
def get_books(request):
    '''
    View return all books
    '''
    if request.method == 'GET':
        books_raw = list(Book.objects.raw(
            "SELECT * FROM book_book"))
        books = [{"id": r.id, "number_serie": r.number_serie,
                  "name": r.name, "category": Category.objects.get(pk=r.category_book_id).category,
                  "resume": r.resume} for r in books_raw]
        return JsonResponse({"data": books}, safe=False)
    return None


@login_required(login_url='/signin')
def save_book(request):
    '''
    View save a book
    '''
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "Book category."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})
    return None


@login_required(login_url='/signin')
def edit_book(request, book_id):
    '''
    View edit a book
    '''
    book_edit = Book.objects.get(pk=id)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book_edit)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "1", "type": "success", "message": "Book edited."})
        return JsonResponse({"status": "-1", "type": "error", "message": "Form not valid."})
    return None


@login_required(login_url='/signin')
def delete_book(request):
    '''
    View delete a book
    '''
    if request.method == 'POST':
        id_book = request.POST['delete_book_id']
        book_delete = Book.objects.get(pk=id_book)
        book_delete.delete()
        return JsonResponse({"status": "1", "type": "success", "message": "Book deleted."})
    return None
