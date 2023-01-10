from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from pajelingo import settings
from pajelingo.tokens import account_activation_token

SIGN_UP_SUBJECT = "Pajelingo account activation"
SIGN_UP_MESSAGE = "Hi {},\n\nPlease click on the link below to activate your Pajelingo account:\n\nhttp://{}{}"
RESET_SUBJECT = "Pajelingo - reset account"
RESET_MESSAGE = "Hi {},\n\nA password reset was requested to your Pajelingo account. " \
                "If it was you who request it, please access the following link:\n\n" \
                "http://{}{}\n\nIf you did not ask for a password reset, please ignore this email."

def request_contains(method, params):
    """
    Verifies if a request method contains the variables whose name is specified as a list in the 'variables_required' argument.

    :param method: HTTP request method
    :type method: dict
    :param params: list of parameters that we want to verify that are contained in the request
    :type params: list

    :return: boolean indicating if all the specified parameters are contained in the request
    """
    dict_values = {}
    for variable in method:
        dict_values[variable] = True

    for variable_required in params:
        if dict_values.get(variable_required) is None:
            return False

    return True


def send_activation_account_email(request, user):
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    url = reverse("activate-account", kwargs={"uidb64": uid, "token": token})

    send_mail(SIGN_UP_SUBJECT, SIGN_UP_MESSAGE.format(user.username, domain, url), settings.EMAIL_FROM, [user.email])


def send_reset_account_email(request, user):
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = reverse("reset-account", kwargs={"uidb64": uid, "token": token})

    send_mail(RESET_SUBJECT, RESET_MESSAGE.format(user.username, domain, url), settings.EMAIL_FROM, [user.email])
