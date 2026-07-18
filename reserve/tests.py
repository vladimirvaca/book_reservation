'''
Tests for reserve app: model, form, and JSON views.
'''
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from book.models import Book
from category.models import Category
from testutils import LoginRequiredTestsMixin

from .forms import ReservationForm
from .models import Reservation

PASSWORD = 'Str0ng-Pass-2026'


def create_book(name='Dune'):
    category = Category.objects.create(category='Fiction', description='Novels')
    return Book.objects.create(
        number_serie='A-001', name=name,
        category_book=category, resume='Desert planet epic')


class ReservationModelTests(TestCase):
    '''
    Model behaviour of Reservation.
    '''

    def test_str_combines_reader_and_book(self):
        book = create_book()
        reservation = Reservation.objects.create(
            dni='123', name='Reader One', book=book)
        self.assertEqual(str(reservation), 'Reader One — Dune')

    def test_defaults(self):
        book = create_book()
        reservation = Reservation.objects.create(
            dni='123', name='Reader One', book=book)
        self.assertEqual(reservation.status, Reservation.STATUS_RESERVED)
        self.assertEqual(reservation.start_date, datetime.date.today())
        self.assertIsNone(reservation.end_date)
        self.assertIsNotNone(reservation.reserved_at)

    def test_deleting_book_cascades_to_reservations(self):
        book = create_book()
        Reservation.objects.create(dni='123', name='Reader One', book=book)
        book.delete()
        self.assertEqual(Reservation.objects.count(), 0)


class ReservationFormTests(TestCase):
    '''
    Validation rules of ReservationForm.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.book = create_book()

    def valid_data(self, **overrides):
        today = datetime.date.today()
        data = {
            'dni': '12345678',
            'name': 'Reader One',
            'book': self.book.pk,
            'start_date': today,
            'end_date': today + datetime.timedelta(days=7),
        }
        data.update(overrides)
        return data

    def test_valid_data(self):
        form = ReservationForm(self.valid_data())
        self.assertTrue(form.is_valid())

    def test_all_fields_required(self):
        for field in ['dni', 'name', 'book', 'start_date', 'end_date']:
            with self.subTest(field=field):
                form = ReservationForm(self.valid_data(**{field: ''}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_end_date_before_start_is_invalid(self):
        today = datetime.date.today()
        form = ReservationForm(self.valid_data(
            end_date=today - datetime.timedelta(days=1)))
        self.assertFalse(form.is_valid())
        self.assertIn('End date must be after start date.',
                      form.non_field_errors())

    def test_end_date_equal_to_start_is_invalid(self):
        form = ReservationForm(self.valid_data(
            end_date=datetime.date.today()))
        self.assertFalse(form.is_valid())


class PublicReservationViewsTests(TestCase):
    '''
    save_reservation and the book list are public endpoints
    (used by the reservation form on the landing page).
    '''

    @classmethod
    def setUpTestData(cls):
        cls.book = create_book()

    def test_save_reservation_creates_record_without_login(self):
        today = datetime.date.today()
        response = self.client.post(reverse('reserve_save'), {
            'dni': '12345678',
            'name': 'Reader One',
            'book': self.book.pk,
            'start_date': today,
            'end_date': today + datetime.timedelta(days=7),
        })
        self.assertEqual(response.json()['status'], '1')
        self.assertEqual(Reservation.objects.count(), 1)

    def test_save_reservation_invalid_form_returns_error(self):
        response = self.client.post(reverse('reserve_save'), {
            'dni': '', 'name': '', 'book': '',
            'start_date': '', 'end_date': ''})
        self.assertEqual(response.json()['status'], '-1')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_get_books_returns_book_list_without_login(self):
        response = self.client.get(reverse('reserve_books'))
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Dune')


class ReservationViewsAuthTests(LoginRequiredTestsMixin, TestCase):
    '''
    Management views require an authenticated user.
    '''

    def get_protected_urls(self):
        return [
            reverse('reserve_get'),
            reverse('reserve_update', args=[1]),
            reverse('reserve_delete'),
        ]


class ReservationManagementViewsTests(TestCase):
    '''
    Listing, updating, and deleting reservations for a logged-in user.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)
        cls.book = create_book()
        today = datetime.date.today()
        cls.reservation = Reservation.objects.create(
            dni='123', name='Reader One', book=cls.book,
            start_date=today, end_date=today + datetime.timedelta(days=7))

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_reservations_returns_data(self):
        response = self.client.get(reverse('reserve_get'))
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Reader One')
        self.assertEqual(data[0]['book'], 'Dune')
        self.assertEqual(data[0]['status'], Reservation.STATUS_RESERVED)

    def test_get_reservations_flags_overdue(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.reservation.end_date = yesterday
        self.reservation.save()
        response = self.client.get(reverse('reserve_get'))
        self.assertEqual(response.json()['data'][0]['status'], 'overdue')

    def test_get_reservations_returned_is_never_overdue(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.reservation.end_date = yesterday
        self.reservation.status = Reservation.STATUS_RETURNED
        self.reservation.save()
        response = self.client.get(reverse('reserve_get'))
        self.assertEqual(
            response.json()['data'][0]['status'],
            Reservation.STATUS_RETURNED)

    def test_update_reservation_changes_status(self):
        response = self.client.post(
            reverse('reserve_update', args=[self.reservation.pk]),
            {'status': Reservation.STATUS_CHECKED_OUT})
        self.assertEqual(response.json()['status'], '1')
        self.reservation.refresh_from_db()
        self.assertEqual(
            self.reservation.status, Reservation.STATUS_CHECKED_OUT)

    def test_update_reservation_rejects_invalid_status(self):
        response = self.client.post(
            reverse('reserve_update', args=[self.reservation.pk]),
            {'status': 'lost'})
        self.assertEqual(response.json()['status'], '-1')
        self.reservation.refresh_from_db()
        self.assertEqual(
            self.reservation.status, Reservation.STATUS_RESERVED)

    def test_update_reservation_unknown_id_returns_error(self):
        response = self.client.post(
            reverse('reserve_update', args=[99999]),
            {'status': Reservation.STATUS_RETURNED})
        self.assertEqual(response.json()['status'], '-1')

    def test_delete_reservation_removes_record(self):
        response = self.client.post(reverse('reserve_delete'), {
            'delete_reservation_id': self.reservation.pk})
        self.assertEqual(response.json()['status'], '1')
        self.assertEqual(Reservation.objects.count(), 0)

    def test_delete_reservation_unknown_id_returns_error(self):
        response = self.client.post(reverse('reserve_delete'), {
            'delete_reservation_id': 99999})
        self.assertEqual(response.json()['status'], '-1')
