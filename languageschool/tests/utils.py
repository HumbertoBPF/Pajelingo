import base64
import random
import string

from django.contrib import auth
from django.db.models import Sum
from django.urls import reverse
from django.utils.crypto import get_random_string

from languageschool.models import Score, Language, Game, User, Badge

TOKEN_URL = reverse("user-token-api")


def is_user_authenticated(client, user):
    """
    Verifies if the specified user is authenticated in the current session.

    :param client: Django client fixture
    :param user: instance of a user that we want to check that is authenticated
    :type user: User

    :return: boolean indicating if the specified user is authenticated
    """
    return auth.get_user(client).username == user.username


def get_user_token(api_client, user, password):
    """
    Gets the token of the specified user.

    :param api_client: Django pytest API client fixture
    :param user: user instance
    :param password: password of the specified user
    :type password: str

    :return: if the user is valid, the token of the matched user. If no user matches the specified credentials,
    returns None
    :rtype: str
    """
    response = api_client.post(TOKEN_URL, data={
        "username": user.username,
        "password": password
    })

    return response.data.get("token")


def get_users(accounts):
    """
    Gets list of users associated with the specified list of accounts (an account here is a tuple with the user object
    and its corresponding password).
    :param accounts: list of tuples, each one containing a user object and its associated password
    :type accounts: list

    :return: list of users
    """
    users = []
    for user, password in accounts:
        users.append(user)

    return users


def get_valid_password():
    """
    Gets a random valid password. A valid password has a length between 8 and 30.

    :return: a random valid password
    """
    return password_factory(random.randint(8, 30), True, True, True)


def get_random_email():
    """
    Gets a random email address. A fake "@test.com" suffix is used.

    :return: a random email address
    """
    return get_random_string(random.randint(8, 32)) + "@test.com"


def get_too_short_username(blank=False):
    min_length = 0 if blank else 1
    return get_random_string(random.randint(min_length, 7))


def get_random_username():
    """
    Gets a random username.

    :return: the random username
    """
    return get_random_string(random.randint(8, 32))


def get_random_bio():
    """
    Gets a random bio.

    :return: the random bio
    """
    return get_random_string(random.randint(1, 500))


def get_too_short_password():
    """
    Gets a password with less than 8 characters, which is below the minimal length.

    :return: a too short password
    """
    return password_factory(random.randint(3, 7), True, True, True)


def get_too_long_password():
    """
    Gets a password with more than 30 characters, which is above the maximal length.

    :return: a too long password
    """
    return password_factory(random.randint(31, 50), True, True, True)


def get_password_without_letters():
    """
    Gets a random password without letters (alphabetic characters).

    :return: a random password without letters
    """
    return password_factory(random.randint(8, 30), False, True, True)


def get_password_without_digits():
    """
    Gets a random password without digits.

    :return: a random password without digits
    """
    return password_factory(random.randint(8, 30), True, False, True)


def get_password_without_special_characters():
    """
    Gets a random password without special characters.

    :return: a random password without special characters
    """
    return password_factory(random.randint(8, 30), True, True, False)


def password_factory(length, has_letters, has_digits, has_special_character):
    password = ""
    allowed_chars = ""

    if has_letters:
        allowed_chars += string.ascii_letters
        password += get_random_string(1, string.ascii_letters)

    if has_digits:
        allowed_chars += string.digits
        password +=  get_random_string(1, string.digits)

    if has_special_character:
        allowed_chars += string.punctuation
        password += get_random_string(1, string.punctuation)

    if length < len(password):
        return get_random_string(length, password)

    return password + get_random_string(length - len(password), allowed_chars)


def assert_badges(badges, user):
    for badge in badges:
        assert user.badges.filter(
            name=badge.get("name"),
            description=badge.get("description"),
            color=badge.get("color")
        ).exists()


def get_ranking(language):
    scores = Score.objects.filter(language=language).values('user__username')\
        .annotate(score=Sum('score')).order_by('-score')

    i = 1
    for score in scores:
        score["position"] = i
        i += 1

    return scores


def get_alphabetically_ordered_url(base_url, query_params):
    keys = list(query_params.keys())

    if len(keys) == 0:
        return base_url

    keys.sort()
    url = "{}?{}={}".format(base_url, keys[0], query_params.get(keys[0]))

    for i in range(1, len(keys)):
        key = keys[i]
        url = "{}&{}={}".format(url, key, query_params.get(key))

    return url


def get_conjugation_game_answer(conjugation):
    language = conjugation.word.language

    return f"{language.personal_pronoun_1} {conjugation.conjugation_1}\n" \
           f"{language.personal_pronoun_2} {conjugation.conjugation_2}\n" \
           f"{language.personal_pronoun_3} {conjugation.conjugation_3}\n" \
           f"{language.personal_pronoun_4} {conjugation.conjugation_4}\n" \
           f"{language.personal_pronoun_5} {conjugation.conjugation_5}\n" \
           f"{language.personal_pronoun_6} {conjugation.conjugation_6}\n"


def get_vocabulary_game_answer(word, base_language):
    synonym_in_base_language = word.synonyms.filter(language__id=base_language.id).values("word_name")

    if len(synonym_in_base_language) == 0:
        return ""
    else:
        return synonym_in_base_language[0].get("word_name")


def achieve_explorer_badge(user):
    languages = Language.objects.all()
    games = Game.objects.all()
    random_language = random.choice(languages)

    for game in games:
        Score.objects.create(
            user=user,
            language=random_language,
            game=game,
            score=1
        )


def attribute_user_badges():
    users = User.objects.all()
    badges = Badge.objects.all()

    for user in users:
        user_badges = random.sample(list(badges.values_list("id", flat=True)), k=2)
        user.badges.add(*user_badges)


def get_profile_picture_base64(user):
    if user.picture:
        img = user.picture.open("rb")
        return base64.b64encode(img.read())
