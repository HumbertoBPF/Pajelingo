from django.contrib import auth, messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from languageschool.forms import FormPicture, PasswordResetForm, SetPasswordForm, UserForm, LoginForm
from languageschool.models import AppUser, Score, Language
from languageschool.utils import send_activation_account_email
from pajelingo import settings
from pajelingo.tokens import account_activation_token

LOGIN_ERROR = "Incorrect username or password. If you are sure that the username and the password are correct, make " \
              "sure that you have activated your account by clicking on the link sent via email."
SUCCESSFUL_SIGN_UP = "User successfully created"
LOGIN_URL = "/account/login"
SUCCESSFUL_ACTIVATION = "Thank you for your email confirmation. Now you can login your account."
ACTIVATION_LINK_ERROR = "Activation link is invalid!"


def load_profile_data(request):
    language_name = request.GET.get("language")
    language = Language.objects.filter(language_name=language_name).first()
    languages = Language.objects.all()

    if language is None:
        language = languages.first()

    scores = None
    if language is not None:
        scores = Score.objects.filter(user=request.user, language=language).order_by('game')

    return {
        "scores": scores,
        "app_user": AppUser.objects.filter(user=request.user)[0],
        "languages": languages,
        "language": language
    }


@require_http_methods(["GET", "POST"])
def signup(request):
    if not request.user.is_authenticated:
        if request.method == "GET":
            user_form = UserForm()
        else:
            user_form = UserForm(request.POST)

            if user_form.is_valid():
                user = user_form.save()
                user.is_active = False
                user.save()
                send_activation_account_email(request, user)
                messages.success(request, SUCCESSFUL_SIGN_UP)

        return render(request, 'account/signup/signup.html', {
            'user_form': user_form
        })
    return redirect('index')

@require_http_methods(["GET", "POST"])
def login(request):
    if not request.user.is_authenticated:
        if request.method == "GET":
            context = {"login_form": LoginForm()}

            next_url = request.GET.get("next")
            if next_url is not None:
                context["next"] = next_url
        else:
            login_form = LoginForm(request.POST)
            context = {"login_form": LoginForm()}

            if login_form.is_valid():
                username = login_form.cleaned_data.get("username")
                password = login_form.cleaned_data.get("password")

                user = auth.authenticate(request, username=username, password=password)

                if user is not None:
                    auth.login(request, user)
                    next_url = request.POST.get("next")
                    if next_url is None:
                        return redirect('index')
                    else:
                        return redirect(next_url)

                messages.error(request, LOGIN_ERROR)

        return render(request, 'account/login.html', context)
    return redirect('index')

@require_GET
def logout(request):
    auth.logout(request)
    return redirect('index')

@require_http_methods(["GET", "POST"])
@login_required(login_url=LOGIN_URL)
def profile(request):
    context = load_profile_data(request)
    if request.method == "GET":
        context["form_picture"] = FormPicture()
    else:
        form_picture = FormPicture(request.POST, request.FILES)

        if form_picture.is_valid():
            app_user = get_object_or_404(AppUser, user=request.user)
            app_user.picture = form_picture.cleaned_data.get('picture')
            app_user.save()
            return redirect("profile")
        else:
            context["form_picture"] = form_picture

    return render(request, 'account/profile.html', context)

@require_http_methods(["GET", "POST"])
@login_required(login_url=LOGIN_URL)
def update_user(request):
    user = User.objects.filter(pk=request.user.id).first()

    if request.method == "GET":
        user_form = UserForm(instance=user)
    else:
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password')
            user_form.save()
            # Login of the user with the new information(if it is not done, the user is automatically logged out)
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
            return redirect("profile")

    return render(request, 'account/update_user.html', {
        'user_form': user_form
    })

@require_POST
@login_required(login_url=LOGIN_URL)
def delete_user(request):
    request.user.delete()
    return redirect('index')

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
