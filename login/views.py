'''
All views from login app.
'''
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import AdminEditForm, AdminForm, LoguinForm

SUPERUSER_ONLY = {"status": "-1", "type": "error",
                  "message": "Only a super admin can manage admins."}


def form_errors_message(form):
    '''
    Flatten form errors into a single toast-friendly message
    '''
    errors = []
    for field, messages in form.errors.items():
        label = form.fields[field].label if field in form.fields else None
        errors.append(f"{label}: {messages[0]}" if label else messages[0])
    return " ".join(errors)


def index(request):
    '''
    View for load index page
    '''
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')


def signin_user(request):
    '''
    View for validating user
    '''
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoguinForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if not get_user_model().objects.filter(username=username).exists():
                return JsonResponse({"status": "0", "type": "error",
                                     "message": f"The user '{username}' does not exist."})
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"status": "1", "type": "info", "message": "User logged."})
            return JsonResponse({"status": "0", "type": "warn",
                                 "message": "Incorrect password."})
        return JsonResponse({"status": "-1", "type": "warn", "message": "Verify all inputs."})
    return render(request, 'login.html')


@login_required(login_url='/signin')
def admins(request):
    '''
    Render principal page of admins. Restricted to superusers.
    '''
    if not request.user.is_superuser:
        return redirect('dashboard')
    return render(request, 'admins.html')


@login_required(login_url='/signin')
def get_admins(request):
    '''
    Get all admin users. Restricted to superusers.
    '''
    if not request.user.is_superuser:
        return JsonResponse({"data": []})
    if request.method == 'GET':
        data = [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_superuser': user.is_superuser,
            'last_login': (user.last_login.strftime('%Y-%m-%d %H:%M')
                           if user.last_login else 'Never'),
        } for user in get_user_model().objects.order_by('username')]
        return JsonResponse({"data": data}, safe=False)
    return None


@login_required(login_url='/signin')
def save_admin(request):
    '''
    View for creating a new admin user. Restricted to superusers.
    '''
    if not request.user.is_superuser:
        return JsonResponse(SUPERUSER_ONLY)
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            return JsonResponse({"status": "1", "type": "success",
                                 "message": f"Admin '{user.username}' created."})
        return JsonResponse({"status": "-1", "type": "error",
                             "message": form_errors_message(form)})
    return None


@login_required(login_url='/signin')
def edit_admin(request, admin_id):
    '''
    Edit an admin user. Restricted to superusers; super admin
    accounts themselves can only be changed via Django admin.
    '''
    if not request.user.is_superuser:
        return JsonResponse(SUPERUSER_ONLY)
    if request.method == 'POST':
        user_model = get_user_model()
        try:
            admin_edit = user_model.objects.get(pk=admin_id)
        except user_model.DoesNotExist:
            return JsonResponse({"status": "-1", "type": "error",
                                 "message": "Admin not found."})
        if admin_edit.is_superuser:
            return JsonResponse({"status": "-1", "type": "error",
                                 "message": "Super admin accounts cannot be edited here."})
        form = AdminEditForm(request.POST, instance=admin_edit)
        if not form.is_valid():
            return JsonResponse({"status": "-1", "type": "error",
                                 "message": form_errors_message(form)})
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if password1 or password2:
            if password1 != password2:
                return JsonResponse({"status": "-1", "type": "error",
                                     "message": "The two password fields didn't match."})
            try:
                validate_password(password1, admin_edit)
            except ValidationError as error:
                return JsonResponse({"status": "-1", "type": "error",
                                     "message": " ".join(error.messages)})
        user = form.save()
        if password1:
            user.set_password(password1)
            user.save()
        return JsonResponse({"status": "1", "type": "success",
                             "message": f"Admin '{user.username}' edited."})
    return None


@login_required(login_url='/signin')
def delete_admin(request):
    '''
    Delete an admin user. Restricted to superusers; blocks deleting
    yourself and other super admin accounts.
    '''
    if not request.user.is_superuser:
        return JsonResponse(SUPERUSER_ONLY)
    if request.method == 'POST':
        user_model = get_user_model()
        try:
            admin_delete = user_model.objects.get(pk=request.POST['delete_admin_id'])
        except user_model.DoesNotExist:
            return JsonResponse({"status": "-1", "type": "error",
                                 "message": "Admin not found."})
        if admin_delete.pk == request.user.pk:
            return JsonResponse({"status": "-1", "type": "error",
                                 "message": "You cannot delete your own account."})
        if admin_delete.is_superuser:
            return JsonResponse({"status": "-1", "type": "error",
                                 "message": "Super admin accounts cannot be deleted here."})
        username = admin_delete.username
        admin_delete.delete()
        return JsonResponse({"status": "1", "type": "success",
                             "message": f"Admin '{username}' deleted."})
    return None


@login_required(login_url='/signin')
def dashboard(request):
    '''
    View for load dashboard page
    '''
    from book.models import Book
    from category.models import Category
    from reserve.models import Reservation
    active_statuses = [Reservation.STATUS_RESERVED, Reservation.STATUS_CHECKED_OUT]
    context = {
        'book_count': Book.objects.count(),
        'category_count': Category.objects.count(),
        'reservation_count': Reservation.objects.filter(status__in=active_statuses).count(),
    }
    return render(request, 'dashboard.html', context)
