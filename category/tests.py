'''
Tests for category app: model, form, and JSON views.
'''
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from testutils import LoginRequiredTestsMixin

from .forms import CategoryForm
from .models import Category

PASSWORD = 'Str0ng-Pass-2026'


class CategoryModelTests(TestCase):
    '''
    Model behaviour of Category.
    '''

    def test_str_returns_category_name(self):
        category = Category.objects.create(category='Fiction', description='Novels')
        self.assertEqual(str(category), 'Fiction')


class CategoryFormTests(TestCase):
    '''
    Validation rules of CategoryForm.
    '''

    def test_valid_data(self):
        form = CategoryForm({'category': 'Fiction', 'description': 'Novels'})
        self.assertTrue(form.is_valid())

    def test_missing_category_is_invalid(self):
        form = CategoryForm({'category': '', 'description': 'Novels'})
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)

    def test_missing_description_is_invalid(self):
        form = CategoryForm({'category': 'Fiction', 'description': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)


class CategoryViewsAuthTests(LoginRequiredTestsMixin, TestCase):
    '''
    All category views require an authenticated user.
    '''

    def get_protected_urls(self):
        return [
            reverse('category'),
            reverse('category_save'),
            reverse('category_get'),
            reverse('category_get_search'),
            reverse('category_edit', args=[1]),
            reverse('category_delete'),
        ]


class CategoryViewsTests(TestCase):
    '''
    CRUD behaviour of the category JSON views for a logged-in user.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)
        cls.category = Category.objects.create(
            category='Fiction', description='Novels')

    def setUp(self):
        self.client.force_login(self.user)

    def test_category_page_renders(self):
        response = self.client.get(reverse('category'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'category.html')

    def test_get_categories_returns_all(self):
        Category.objects.create(category='Science', description='Research')
        response = self.client.get(reverse('category_get'))
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(len(data), 2)
        self.assertEqual({c['category'] for c in data}, {'Fiction', 'Science'})

    def test_save_category_creates_record(self):
        response = self.client.post(reverse('category_save'), {
            'category': 'History', 'description': 'Past events'})
        self.assertEqual(response.json()['status'], '1')
        self.assertTrue(Category.objects.filter(category='History').exists())

    def test_save_category_invalid_form_returns_error(self):
        response = self.client.post(reverse('category_save'), {
            'category': '', 'description': ''})
        self.assertEqual(response.json()['status'], '-1')
        self.assertEqual(Category.objects.count(), 1)

    def test_edit_category_updates_record(self):
        response = self.client.post(
            reverse('category_edit', args=[self.category.pk]),
            {'category': 'Fiction & Fantasy', 'description': 'Updated'})
        self.assertEqual(response.json()['status'], '1')
        self.category.refresh_from_db()
        self.assertEqual(self.category.category, 'Fiction & Fantasy')
        self.assertEqual(self.category.description, 'Updated')

    def test_edit_category_invalid_form_keeps_record(self):
        response = self.client.post(
            reverse('category_edit', args=[self.category.pk]),
            {'category': '', 'description': ''})
        self.assertEqual(response.json()['status'], '-1')
        self.category.refresh_from_db()
        self.assertEqual(self.category.category, 'Fiction')

    def test_search_filters_by_criteria_case_insensitive(self):
        Category.objects.create(category='Science', description='Research')
        response = self.client.get(
            reverse('category_get_search'), {'criteria': 'fic'})
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['category'], 'Fiction')

    def test_search_without_criteria_returns_at_most_five(self):
        for i in range(6):
            Category.objects.create(category=f'Extra {i}', description='filler')
        response = self.client.get(reverse('category_get_search'))
        self.assertEqual(len(response.json()), 5)

    def test_delete_category_removes_record(self):
        response = self.client.post(reverse('category_delete'), {
            'delete_category_id': self.category.pk})
        self.assertEqual(response.json()['status'], '1')
        self.assertFalse(Category.objects.filter(pk=self.category.pk).exists())
