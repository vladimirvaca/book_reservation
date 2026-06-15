import datetime

from django.db import models

from book.models import Book


class Reservation(models.Model):
    STATUS_RESERVED = 'reserved'
    STATUS_CHECKED_OUT = 'checked_out'
    STATUS_RETURNED = 'returned'

    STATUS_CHOICES = [
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_CHECKED_OUT, 'Checked Out'),
        (STATUS_RETURNED, 'Returned'),
    ]

    dni = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(null=True, blank=True)
    reserved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RESERVED)

    def __str__(self):
        return f'{self.name} — {self.book.name}'
