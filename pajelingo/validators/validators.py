from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

ERROR_USERNAME_FORMAT = "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
ERROR_NOT_CONFIRMED_PASSWORD = "The passwords do not match."
ERROR_NOT_AVAILABLE_EMAIL = "This email is not available."
ERROR_NOT_AVAILABLE_USERNAME = "A user with that username already exists."
ERROR_REQUIRED_FIELD = "This field is required."
ERROR_EMAIL_FORMAT = "Enter a valid email address."
ERROR_IMAGE_FILE_FORMAT = "Upload a valid image. The file you uploaded was either not an image or a corrupted image."
ERROR_USERNAME_LENGTH = "The username must be at least 8 characters-long."


def validate_email(email, instance):
    """
    Verifies if the specified email is available, that is, if it has not been taken by another user yet.

    :param email: email input.
    :type email: str
    :param instance: User instance that is concerned by the email data that we are checking. If the validation is
    performed at creation time, it is empty. Otherwise, the validation is performed at update time and the instance
    should map an existing user.
    :type instance: User
    """
    user_with_email = User.objects.filter(email=email).first()
    if ((instance is None) and (user_with_email is not None)) or \
            ((instance is not None) and (user_with_email is not None) and (user_with_email.id != instance.id)):
        raise ValidationError(ERROR_NOT_AVAILABLE_EMAIL)


def validate_username(username):
    """
    Verifies if the username is at least 8 characters-long.

    :param username: username input.
    :type username: str
    """
    if (username is not None) and (len(username) < 8):
        raise ValidationError(ERROR_USERNAME_LENGTH)