import base64

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import PermissionDenied

from languageschool.models import GameRound, Game
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


def get_base_64_encoded_image(image_file):
    if image_file:
        try:
            img = image_file.open("rb")
            return base64.b64encode(img.read())
        except FileNotFoundError as e:
            print(e)


def save_game_round(request, game_id, round_data):
    game_round = GameRound.objects.filter(game__id=game_id).first()

    if not request.user.is_anonymous:
        if game_round is None:
            GameRound.objects.create(
                game=Game.objects.get(id=game_id),
                user=request.user,
                round_data=round_data
            )
        else:
            game_round.user = request.user
            game_round.round_data = round_data
            game_round.save()


def check_game_round(request, game_id, round_data):
    game_round = GameRound.objects.filter(
        game__id=game_id,
        user=request.user
    ).first()

    if game_round is None:
        raise PermissionDenied()

    if game_round.round_data != round_data:
        raise PermissionDenied()
