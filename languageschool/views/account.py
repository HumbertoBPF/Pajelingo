from django.contrib import auth, messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_GET, require_POST

from languageschool.forms import FormPicture, PasswordResetForm, SetPasswordForm
from languageschool.models import AppUser, Score
from languageschool.validation import is_valid_user_data
from languageschool.views.general import request_contains
from pajelingo import settings
from pajelingo.tokens import account_activation_token

LOGIN_ERROR = "Incorrect username or password"
NOT_ACTIVE_ERROR = "The specified account has not been activated yet. Please check your email and activate it."
SUCCESSFUL_SIGN_UP = "User successfully created"
LOGIN_URL = "/account/login"
SIGN_UP_SUBJECT = "Pajelingo account activation"
SIGN_UP_MESSAGE = "Hi {},\n\nPlease click on the link below to activate your Pajelingo account:\n\nhttp://{}{}"
SUCCESSFUL_ACTIVATION = "Thank you for your email confirmation. Now you can login your account."
ACTIVATION_LINK_ERROR = "Activation link is invalid!"

@require_GET
def signup(request):
    return render(request, 'account/signup/signup.html')

@require_POST
def signup_done(request):
    if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password_confirmation = request.POST["password_confirmation"]
        error_field, error_message = is_valid_user_data(email, username, password, password_confirmation)
        if error_field is None:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.is_active = False
            user.save()

            domain = get_current_site(request).domain
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            url = reverse("activate-account", kwargs={"uidb64": uid, "token": token})

            send_mail(SIGN_UP_SUBJECT, SIGN_UP_MESSAGE.format(username, domain, url), settings.EMAIL_FROM, [email])
            messages.success(request, SUCCESSFUL_SIGN_UP)
            return redirect('signup')
        else:
            messages.error(request, error_message)
    return redirect('signup')

@require_GET
def login(request):
    context = None

    next_url = request.GET.get("next")
    if next_url is not None:
        context = {"next": next_url}

    return render(request, 'account/login.html', context)

@require_POST
def login_done(request):
    if request_contains(request.POST, ["username", "password"]):
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            next_url = request.POST.get("next")
            if next_url is None:
                return redirect('index')
            else:
                return redirect(next_url)
        else:
            user_with_username = User.objects.filter(username=username).first()

            if (user_with_username is not None) and (not user_with_username.is_active):
                messages.error(request, NOT_ACTIVE_ERROR)
            else:
                messages.error(request, LOGIN_ERROR)
    return redirect('login')

@require_GET
def logout(request):
    auth.logout(request)
    return redirect('index')

@require_GET
@login_required(login_url=LOGIN_URL)
def profile(request):
    context = {
        "scores": Score.objects.filter(user=request.user).order_by('language', 'game'),
        "app_user": AppUser.objects.filter(user=request.user)[0],
        "form_picture": FormPicture()
    }
    return render(request, 'account/profile.html', context)

@require_GET
@login_required(login_url=LOGIN_URL)
def update_user(request):
    return render(request, 'account/update_user.html', {'user_id': request.user.id})

@require_POST
@login_required(login_url=LOGIN_URL)
def update_user_done(request):
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
            return redirect('profile')
        else:
            messages.error(request, error_message)
    return redirect('update-user')

@require_POST
@login_required(login_url=LOGIN_URL)
def delete_user(request):
    request.user.delete()
    return redirect('index')

@require_POST
@login_required(login_url=LOGIN_URL)
def change_picture(request):
    form_picture = FormPicture(request.POST, request.FILES)
    if form_picture.is_valid():
        app_user = get_object_or_404(AppUser, user=request.user)
        app_user.picture = form_picture.cleaned_data.get('picture')
        app_user.save()
    return redirect('profile')

@require_GET
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.filter(pk=uid).first()
    except(TypeError, ValueError, OverflowError):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, SUCCESSFUL_ACTIVATION)
    else:
        messages.error(request, ACTIVATION_LINK_ERROR)

    return render(request, "account/signup/activate.html")

class PasswordResetView(auth_views.PasswordResetView):
    template_name = "account/reset_account/request_reset_account.html"
    subject_template_name = "email/reset_email_subject.txt"
    email_template_name = "email/reset_email_body.html"
    success_url = "/account/request-reset-account-done"
    from_email = settings.EMAIL_FROM
    form_class = PasswordResetForm
class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "account/reset_account/request_reset_account_done.html"

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "account/reset_account/reset_account.html"
    success_url = "/account/reset-account-done"
    form_class = SetPasswordForm

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "account/reset_account/reset_account_done.html"
