from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from pajelingo.settings import FRONT_END_URL, EMAIL_FROM
from pajelingo.tokens import account_activation_token

SIGN_UP_SUBJECT = "Pajelingo account activation"
SIGN_UP_MESSAGE = "Hi {},\n\nPlease click on the link below to activate your Pajelingo account:\n\n" \
                  "{}{}"
RESET_SUBJECT = "Pajelingo account reset"
RESET_MESSAGE = "Hi {},\n\nA password reset was requested to your Pajelingo account. " \
                "If it was you who request it, please access the following link:\n\n" \
                "{}{}\n\nIf you did not ask for a password reset, please ignore this email."

def send_activation_account_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    url = "/activate/{}/{}".format(uid, token)

    send_mail(SIGN_UP_SUBJECT, SIGN_UP_MESSAGE.format(user.username, FRONT_END_URL, url), EMAIL_FROM, [user.email])


def send_reset_account_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    url = "/reset-account/{}/{}".format(uid, token)

    send_mail(RESET_SUBJECT, RESET_MESSAGE.format(user.username, FRONT_END_URL, url), EMAIL_FROM, [user.email])
