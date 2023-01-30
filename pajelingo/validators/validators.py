from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

ERROR_SPACE_IN_USERNAME = "Username field cannot contain spaces."
ERROR_NOT_CONFIRMED_PASSWORD = "Passwords do not match."
ERROR_NOT_AVAILABLE_EMAIL = "This email is not available."
ERROR_NOT_AVAILABLE_USERNAME = "A user with that username already exists."
ERROR_IMAGE_FILE_FORMAT = "Upload a valid image. The file you uploaded was either not an image or a corrupted image."


def validate_email(email, instance):
    # Verifying if the specified email is available
    user_with_email = User.objects.filter(email=email).first()
    if ((instance is None) and (user_with_email is not None)) or \
            ((instance is not None) and (user_with_email is not None) and (user_with_email.id != instance.id)):
        raise ValidationError(ERROR_NOT_AVAILABLE_EMAIL)

def validate_username(username):
    # Verifying if username contains spaces
    if username.find(" ") != -1:
        raise ValidationError(ERROR_SPACE_IN_USERNAME)
