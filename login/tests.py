'''
Tests for login app: authentication flow, admin management, and dashboard.
'''
import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from book.models import Book
from category.models import Category
from reserve.models import Reservation

PASSWORD = 'Str0ng-Pass-2026'


class IndexViewTests(TestCase):
    '''
    Behaviour of the public index page.
    '''

    def test_anonymous_user_sees_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_authenticated_user_is_redirected_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)
        self.client.force_login(user)
        response = self.client.get(reverse('index'))
        self.assertRedirects(response, reverse('dashboard'))


class SigninViewTests(TestCase):
    '''
    Behaviour of the signin view (page render and JSON login endpoint).
    '''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)

    def test_get_renders_login_page(self):
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_authenticated_user_is_redirected_to_dashboard(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('signin'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_valid_credentials_log_the_user_in(self):
        response = self.client.post(reverse('signin'), {
            'username': 'librarian', 'password': PASSWORD})
        self.assertEqual(response.json()['status'], '1')
        self.assertEqual(
            int(self.client.session['_auth_user_id']), self.user.pk)

    def test_nonexistent_user_returns_error(self):
        response = self.client.post(reverse('signin'), {
            'username': 'ghost', 'password': PASSWORD})
        payload = response.json()
        self.assertEqual(payload['status'], '0')
        self.assertIn('does not exist', payload['message'])

    def test_wrong_password_returns_warning(self):
        response = self.client.post(reverse('signin'), {
            'username': 'librarian', 'password': 'wrong-password'})
        payload = response.json()
        self.assertEqual(payload['status'], '0')
        self.assertEqual(payload['type'], 'warn')

    def test_missing_fields_return_form_error(self):
        response = self.client.post(reverse('signin'), {
            'username': '', 'password': ''})
        self.assertEqual(response.json()['status'], '-1')


class AdminAccessTests(TestCase):
    '''
    Admin management is restricted to superusers.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_user(
            username='staff', password=PASSWORD)

    def test_anonymous_user_is_redirected_to_signin(self):
        response = self.client.get(reverse('admins'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/signin'))

    def test_non_superuser_is_redirected_from_admins_page(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admins'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_non_superuser_gets_empty_admin_list(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin_get'))
        self.assertEqual(response.json()['data'], [])

    def test_non_superuser_cannot_save_admin(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('admin_save'), {
            'username': 'newadmin',
            'password1': PASSWORD, 'password2': PASSWORD})
        self.assertEqual(response.json()['status'], '-1')
        self.assertFalse(
            get_user_model().objects.filter(username='newadmin').exists())

    def test_non_superuser_cannot_edit_admin(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_edit', args=[self.staff.pk]),
            {'username': 'renamed'})
        self.assertEqual(response.json()['status'], '-1')

    def test_non_superuser_cannot_delete_admin(self):
        self.client.force_login(self.staff)
        response = self.client.post(reverse('admin_delete'), {
            'delete_admin_id': self.staff.pk})
        self.assertEqual(response.json()['status'], '-1')
        self.assertTrue(
            get_user_model().objects.filter(pk=self.staff.pk).exists())


class AdminManagementTests(TestCase):
    '''
    Admin CRUD behaviour for a logged-in superuser.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.superuser = get_user_model().objects.create_superuser(
            username='root', password=PASSWORD)
        cls.admin = get_user_model().objects.create_user(
            username='helper', password=PASSWORD, is_staff=True)

    def setUp(self):
        self.client.force_login(self.superuser)

    def test_admins_page_renders(self):
        response = self.client.get(reverse('admins'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admins.html')

    def test_get_admins_lists_all_users(self):
        response = self.client.get(reverse('admin_get'))
        data = response.json()['data']
        self.assertEqual([u['username'] for u in data], ['helper', 'root'])
        self.assertEqual(
            [u['is_superuser'] for u in data], [False, True])

    def test_get_admins_shows_never_for_no_last_login(self):
        response = self.client.get(reverse('admin_get'))
        helper = next(u for u in response.json()['data']
                      if u['username'] == 'helper')
        self.assertEqual(helper['last_login'], 'Never')

    def test_save_admin_creates_staff_user(self):
        response = self.client.post(reverse('admin_save'), {
            'username': 'newadmin', 'email': 'new@example.com',
            'password1': PASSWORD, 'password2': PASSWORD})
        self.assertEqual(response.json()['status'], '1')
        user = get_user_model().objects.get(username='newadmin')
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password(PASSWORD))

    def test_save_admin_rejects_duplicate_username(self):
        response = self.client.post(reverse('admin_save'), {
            'username': 'helper',
            'password1': PASSWORD, 'password2': PASSWORD})
        self.assertEqual(response.json()['status'], '-1')

    def test_save_admin_rejects_password_mismatch(self):
        response = self.client.post(reverse('admin_save'), {
            'username': 'newadmin',
            'password1': PASSWORD, 'password2': 'Different-Pass-1'})
        self.assertEqual(response.json()['status'], '-1')
        self.assertFalse(
            get_user_model().objects.filter(username='newadmin').exists())

    def test_edit_admin_updates_username_and_email(self):
        response = self.client.post(
            reverse('admin_edit', args=[self.admin.pk]),
            {'username': 'renamed', 'email': 'renamed@example.com'})
        self.assertEqual(response.json()['status'], '1')
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.username, 'renamed')
        self.assertEqual(self.admin.email, 'renamed@example.com')

    def test_edit_admin_changes_password_when_provided(self):
        new_password = 'An0ther-Pass-2026'
        response = self.client.post(
            reverse('admin_edit', args=[self.admin.pk]),
            {'username': 'helper',
             'password1': new_password, 'password2': new_password})
        self.assertEqual(response.json()['status'], '1')
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password(new_password))

    def test_edit_admin_rejects_password_mismatch(self):
        response = self.client.post(
            reverse('admin_edit', args=[self.admin.pk]),
            {'username': 'helper',
             'password1': PASSWORD, 'password2': 'Different-Pass-1'})
        payload = response.json()
        self.assertEqual(payload['status'], '-1')
        self.assertIn("didn't match", payload['message'])

    def test_edit_admin_rejects_weak_password(self):
        response = self.client.post(
            reverse('admin_edit', args=[self.admin.pk]),
            {'username': 'helper', 'password1': '123', 'password2': '123'})
        self.assertEqual(response.json()['status'], '-1')
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password(PASSWORD))

    def test_edit_admin_cannot_target_superuser(self):
        response = self.client.post(
            reverse('admin_edit', args=[self.superuser.pk]),
            {'username': 'renamed-root'})
        payload = response.json()
        self.assertEqual(payload['status'], '-1')
        self.assertIn('Super admin', payload['message'])

    def test_edit_admin_unknown_id_returns_error(self):
        response = self.client.post(
            reverse('admin_edit', args=[99999]), {'username': 'ghost'})
        self.assertEqual(response.json()['status'], '-1')

    def test_delete_admin_removes_user(self):
        response = self.client.post(reverse('admin_delete'), {
            'delete_admin_id': self.admin.pk})
        self.assertEqual(response.json()['status'], '1')
        self.assertFalse(
            get_user_model().objects.filter(pk=self.admin.pk).exists())

    def test_delete_admin_blocks_own_account(self):
        response = self.client.post(reverse('admin_delete'), {
            'delete_admin_id': self.superuser.pk})
        payload = response.json()
        self.assertEqual(payload['status'], '-1')
        self.assertIn('own account', payload['message'])

    def test_delete_admin_blocks_other_superusers(self):
        other = get_user_model().objects.create_superuser(
            username='root2', password=PASSWORD)
        response = self.client.post(reverse('admin_delete'), {
            'delete_admin_id': other.pk})
        self.assertEqual(response.json()['status'], '-1')
        self.assertTrue(
            get_user_model().objects.filter(pk=other.pk).exists())

    def test_delete_admin_unknown_id_returns_error(self):
        response = self.client.post(reverse('admin_delete'), {
            'delete_admin_id': 99999})
        self.assertEqual(response.json()['status'], '-1')


class DashboardViewTests(TestCase):
    '''
    Dashboard renders and reports correct entity counts.
    '''

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)
        category = Category.objects.create(
            category='Fiction', description='Novels')
        book = Book.objects.create(
            number_serie='A-001', name='Dune',
            category_book=category, resume='Desert planet epic')
        today = datetime.date.today()
        Reservation.objects.create(
            dni='123', name='Reader One', book=book,
            start_date=today, end_date=today + datetime.timedelta(days=7),
            status=Reservation.STATUS_RESERVED)
        Reservation.objects.create(
            dni='456', name='Reader Two', book=book,
            start_date=today, end_date=today + datetime.timedelta(days=7),
            status=Reservation.STATUS_RETURNED)

    def test_anonymous_user_is_redirected_to_signin(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/signin'))

    def test_dashboard_shows_counts_excluding_returned_reservations(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertEqual(response.context['book_count'], 1)
        self.assertEqual(response.context['category_count'], 1)
        self.assertEqual(response.context['reservation_count'], 1)


class LogoutTests(TestCase):
    '''
    Logout ends the session and redirects to the index page.
    '''

    def test_logout_redirects_to_index(self):
        user = get_user_model().objects.create_user(
            username='librarian', password=PASSWORD)
        self.client.force_login(user)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, '/')
        self.assertNotIn('_auth_user_id', self.client.session)
