import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from book.models import Book

from .forms import ReservationForm
from .models import Reservation


def save_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': '1', 'type': 'success',
                                 'message': 'Book reserved successfully.'})
        return JsonResponse({'status': '-1', 'type': 'error',
                             'message': 'Please fill in all required fields correctly.'})
    return None


def get_books(request):
    if request.method == 'GET':
        books = list(Book.objects.values('id', 'name', 'number_serie'))
        return JsonResponse(books, safe=False)
    return None


@login_required(login_url='/signin')
def get_reservations(request):
    if request.method == 'GET':
        today = datetime.date.today()
        queryset = Reservation.objects.select_related('book').all().order_by('-reserved_at')
        data = []
        for r in queryset:
            overdue = (
                r.status != Reservation.STATUS_RETURNED
                and r.end_date is not None
                and r.end_date < today
            )
            data.append({
                'id': r.id,
                'name': r.name,
                'dni': r.dni,
                'book': r.book.name,
                'start_date': r.start_date.strftime('%Y-%m-%d') if r.start_date else '—',
                'end_date': r.end_date.strftime('%Y-%m-%d') if r.end_date else '—',
                'status': 'overdue' if overdue else r.status,
                'reserved_at': r.reserved_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({'data': data})
    return None


@login_required(login_url='/signin')
def update_reservation(request, reservation_id):
    if request.method == 'POST':
        valid = [Reservation.STATUS_RESERVED, Reservation.STATUS_CHECKED_OUT,
                 Reservation.STATUS_RETURNED]
        new_status = request.POST.get('status')
        if new_status not in valid:
            return JsonResponse({'status': '-1', 'type': 'error', 'message': 'Invalid status.'})
        try:
            reservation = Reservation.objects.get(pk=reservation_id)
            reservation.status = new_status
            reservation.save()
            return JsonResponse({'status': '1', 'type': 'success',
                                 'message': 'Reservation updated successfully.'})
        except Reservation.DoesNotExist:
            return JsonResponse({'status': '-1', 'type': 'error',
                                 'message': 'Reservation not found.'})
    return None


@login_required(login_url='/signin')
def delete_reservation(request):
    if request.method == 'POST':
        reservation_id = request.POST.get('delete_reservation_id')
        try:
            Reservation.objects.get(pk=reservation_id).delete()
            return JsonResponse({'status': '1', 'type': 'success',
                                 'message': 'Reservation cleared successfully.'})
        except Reservation.DoesNotExist:
            return JsonResponse({'status': '-1', 'type': 'error',
                                 'message': 'Reservation not found.'})
    return None
