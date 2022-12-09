from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from languageschool.forms import FormPicture
from languageschool.models import AppUser, Score
from languageschool.utils import require_authentication
from languageschool.validation import is_valid_user_data
from languageschool.views.general import request_contains

LOGIN_ERROR = "Incorrect username or password"
SUCCESSFUL_SIGN_UP = "User successfully created"

@require_GET
def sign_in(request):
    return render(request, 'account/sign_in.html')

@require_POST
def create_user(request):
    if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password_confirmation = request.POST["password_confirmation"]
        error_field, error_message = is_valid_user_data(email, username, password, password_confirmation)
        if error_field is None:
            # Creating admin user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            messages.success(request, SUCCESSFUL_SIGN_UP)
            return redirect('account-sign-in')
        else:
            messages.error(request, error_message)
    return redirect('account-sign-in')

@require_GET
def login(request):
    return render(request, 'account/login.html')

@require_POST
def auth_user(request):
    if request_contains(request.POST, ["username", "password"]):
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, LOGIN_ERROR)
    return redirect('account-login')

@require_GET
def logout(request):
    auth.logout(request)
    return redirect('index')

@require_GET
@require_authentication
def profile(request):
    context = {"scores": Score.objects.filter(user=request.user).order_by('language'),
               "app_user": AppUser.objects.filter(user=request.user)[0], "form_picture": FormPicture()}
    return render(request, 'account/profile.html', context)

@require_GET
@require_authentication
def update_user(request):
    return render(request, 'account/update_user.html', {'user_id': request.user.id})

@require_POST
@require_authentication
def do_update_user(request):
    if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password_confirmation = request.POST["password_confirmation"]
        error_field, error_message = is_valid_user_data(email, username, password, password_confirmation, existing_user=request.user)
        if error_field is None:
            # Update information of the user currently logged in
            request.user.email = email
            request.user.username = username
            request.user.password = make_password(password)
            request.user.save()
            # Login of the user with the new information(if it is not done, the user is automatically logged out)
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
            return redirect('account-profile')
        else:
            messages.error(request, error_message)
    return redirect('account-update-user')

@require_POST
@require_authentication
def delete_user(request):
    request.user.delete()
    return redirect('index')

@require_POST
@require_authentication
def change_picture(request):
    form_picture = FormPicture(request.POST, request.FILES)
    if form_picture.is_valid():
        app_user = get_object_or_404(AppUser, user=request.user)
        app_user.picture = form_picture.cleaned_data.get('picture')
        app_user.save()
    return redirect('account-profile')
