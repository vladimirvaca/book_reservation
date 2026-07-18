'''
Tests for book app: model, form, and JSON views.
'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from category.models import Category
from testutils import LoginRequiredTestsMixin

from .forms import BookForm
from .models import Book

PASSWORD = 'Str0ng-Pass-2026'


class BookModelTests(TestCase):
    '''
    Model behaviour of Book.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            category='Fiction', description='Novels')

    def test_str_returns_book_name(self):
        book = Book.objects.create(
            number_serie='A-001', name='Dune',
            category_book=self.category, resume='Desert planet epic')
        self.assertEqual(str(book), 'Dune')

    def test_deleting_category_cascades_to_books(self):
        Book.objects.create(
            number_serie='A-001', name='Dune',
            category_book=self.category, resume='Desert planet epic')
        self.category.delete()
        self.assertEqual(Book.objects.count(), 0)


class BookFormTests(TestCase):
    '''
    Validation rules of BookForm.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            category='Fiction', description='Novels')

    def valid_data(self, **overrides):
        data = {
            'number_serie': 'A-001',
            'name': 'Dune',
            'category_book': self.category.pk,
            'resume': 'Desert planet epic',
        }
        data.update(overrides)
        return data

    def test_valid_data(self):
        form = BookForm(self.valid_data())
        self.assertTrue(form.is_valid())

    def test_all_fields_required(self):
        for field in ['number_serie', 'name', 'category_book', 'resume']:
            with self.subTest(field=field):
                form = BookForm(self.valid_data(**{field: ''}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_nonexistent_category_is_invalid(self):
        form = BookForm(self.valid_data(category_book=99999))
        self.assertFalse(form.is_valid())
        self.assertIn('category_book', form.errors)


class BookViewsAuthTests(LoginRequiredTestsMixin, TestCase):
    '''
    All book views require an authenticated user.
    '''

    def get_protected_urls(self):
        return [
            reverse('book'),
            reverse('book_save'),
            reverse('get_books'),
            reverse('book_edit', args=[1]),
            reverse('book_delete'),
        ]


class BookViewsTests(TestCase):
    '''
    CRUD behaviour of the book JSON views for a logged-in user.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)
        cls.category = Category.objects.create(
            category='Fiction', description='Novels')
        cls.book = Book.objects.create(
            number_serie='A-001', name='Dune',
            category_book=cls.category, resume='Desert planet epic')

    def setUp(self):
        self.client.force_login(self.user)

    def test_book_page_renders(self):
        response = self.client.get(reverse('book'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book.html')

    def test_get_books_returns_all_with_category_name(self):
        response = self.client.get(reverse('get_books'))
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Dune')
        self.assertEqual(data[0]['category'], 'Fiction')
        self.assertEqual(data[0]['number_serie'], 'A-001')

    def test_save_book_creates_record(self):
        response = self.client.post(reverse('book_save'), {
            'number_serie': 'B-002',
            'name': 'Foundation',
            'category_book': self.category.pk,
            'resume': 'Galactic empire falls',
        })
        self.assertEqual(response.json()['status'], '1')
        self.assertTrue(Book.objects.filter(name='Foundation').exists())

    def test_save_book_invalid_form_returns_error(self):
        response = self.client.post(reverse('book_save'), {
            'number_serie': '', 'name': '', 'category_book': '', 'resume': ''})
        self.assertEqual(response.json()['status'], '-1')
        self.assertEqual(Book.objects.count(), 1)

    def test_edit_book_updates_record(self):
        response = self.client.post(
            reverse('book_edit', args=[self.book.pk]), {
                'number_serie': 'A-001',
                'name': 'Dune Messiah',
                'category_book': self.category.pk,
                'resume': 'The sequel',
            })
        self.assertEqual(response.json()['status'], '1')
        self.book.refresh_from_db()
        self.assertEqual(self.book.name, 'Dune Messiah')
        self.assertEqual(self.book.resume, 'The sequel')

    def test_edit_book_invalid_form_keeps_record(self):
        response = self.client.post(
            reverse('book_edit', args=[self.book.pk]), {
                'number_serie': '', 'name': '',
                'category_book': '', 'resume': ''})
        self.assertEqual(response.json()['status'], '-1')
        self.book.refresh_from_db()
        self.assertEqual(self.book.name, 'Dune')

    def test_delete_book_removes_record(self):
        response = self.client.post(reverse('book_delete'), {
            'delete_book_id': self.book.pk})
        self.assertEqual(response.json()['status'], '1')
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
