from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from languageschool.forms import FormPicture
from languageschool.models import AppUser, Score
from languageschool.validation import is_valid_user_data
from languageschool.views.general import request_contains
from django.contrib.auth.hashers import make_password


def sign_in(request):
    return render(request, 'account/sign_in.html')


def create_user(request):
    if request.method == "POST":
        if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
            email = request.POST["email"]
            username = request.POST["username"]
            password = request.POST["password"]
            password_confirmation = request.POST["password_confirmation"]
            is_valid, error_message = is_valid_user_data(email, username, password, password_confirmation)
            if is_valid:
                # Creating admin user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # Creating app user
                app_user = AppUser(user=user)
                app_user.save()
                messages.success(request, "User successfully created")
                print("User created")
                return redirect('account-sign-in')
            else:
                messages.error(request, error_message)
    return sign_in(request)


def login(request):
    return render(request, 'account/login.html')


def auth_user(request):
    if request.method == "POST":
        if request_contains(request.POST, ["username", "password"]):
            username = request.POST["username"].strip()
            password = request.POST["password"].strip()

            user = auth.authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Incorrect username or password")
    return login(request)


def logout(request):
    auth.logout(request)
    return redirect('index')


def profile(request):
    context = {'scores': []}
    if request.user.is_authenticated:
        context["scores"] = Score.objects.filter(user=request.user).order_by('language')
        context["app_user"] = AppUser.objects.filter(user=request.user)[0]
        context["form_picture"] = FormPicture()
    return render(request, 'account/profile.html', context)


def update_user(request):
    # Users are allowed to update a user info only if they are authenticated in their account.
    if request.user.is_authenticated:
        return render(request, 'account/update_user.html', {'user_id': request.user.id})
    # If the user is not logged, redirect to the index page
    return redirect('index')


def do_update_user(request):
    if request.method == "POST" and request.user.is_authenticated:
        if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
            email = request.POST["email"]
            username = request.POST["username"]
            password = request.POST["password"]
            password_confirmation = request.POST["password_confirmation"]
            is_valid, error_message = is_valid_user_data(email, username, password, password_confirmation, existing_user=request.user)
            if is_valid:
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
    return update_user(request)


def delete_user(request):
    # It is important to be sure that the method was POST in order to avoid users to accidentally delete their accounts by merely accessing this endpoint
    if request.method == "POST" and request.user.is_authenticated:
        request.user.delete()
    return redirect('index')


def change_picture(request):
    if request.method == "POST" and request.user.is_authenticated:
        form_picture = FormPicture(request.POST, request.FILES)
        if form_picture.is_valid():
            app_user = get_object_or_404(AppUser, user=request.user)
            app_user.picture = form_picture.cleaned_data.get('picture')
            app_user.save()
    return redirect('account-profile')
