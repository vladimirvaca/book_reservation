'''
Views for book app
'''
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from .forms import BookForm
from .models import Book


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
        books = [
            {
                "id": b.id,
                "number_serie": b.number_serie,
                "name": b.name,
                "category": b.category_book.category,
                "resume": b.resume,
            }
            for b in Book.objects.select_related('category_book').all()
        ]
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
    book_edit = Book.objects.get(pk=book_id)
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
