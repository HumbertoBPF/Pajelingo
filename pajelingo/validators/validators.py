import abc

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

ERROR_EMPTY_EMAIL = "Email field is mandatory"
ERROR_EMPTY_USERNAME = "Username field is mandatory"
ERROR_SPACE_IN_EMAIL = "Email field cannot contain spaces"
ERROR_SPACE_IN_USERNAME = "Username field cannot contain spaces"
ERROR_NOT_CONFIRMED_PASSWORD = "Passwords do not match"
ERROR_NOT_AVAILABLE_EMAIL = "This email is not available"
ERROR_NOT_AVAILABLE_USERNAME = "This username is not available"

class FieldValidator(abc.ABC):
    @abc.abstractmethod
    def validate(self, field, user=None):
        """
        Method to perform the validation. It should return None if the field data is valid and a ValidationError
        otherwise.

        :param field: field data to be validated
        :param user: User instance to be optionally used in the validation
        :type user: User
        """
        pass

class EmailValidator(FieldValidator):
    def validate(self, email, user=None):
        # Verifying if email is empty
        if (email is None) or (len(email) == 0):
            raise ValidationError(ERROR_EMPTY_EMAIL)
        # Verifying if email contains spaces
        if email.find(" ") != -1:
            raise ValidationError(ERROR_SPACE_IN_EMAIL)
        # Verifying if the specified email is available
        user_with_email = User.objects.filter(email=email).first()
        if ((user is None) and (user_with_email is not None)) or \
                ((user is not None) and (user_with_email is not None) and (user_with_email.id != user.id)):
            raise ValidationError(ERROR_NOT_AVAILABLE_EMAIL)

class UsernameValidator(FieldValidator):
    def validate(self, username, user=None):
        # Verifying if username is empty
        if (username is None) or (len(username) == 0):
            raise ValidationError(ERROR_EMPTY_USERNAME)
        # Verifying if username contains spaces
        if username.find(" ") != -1:
            raise ValidationError(ERROR_SPACE_IN_USERNAME)
        # Verifying if the specified username is available
        user_with_username = User.objects.filter(username=username).first()
        if ((user is None) and (user_with_username is not None)) or \
                ((user is not None) and (user_with_username is not None) and (user_with_username.id != user.id)):
            raise ValidationError(ERROR_NOT_AVAILABLE_USERNAME)

def is_valid_user_data(email, username, password, password_confirmation, existing_user=None):
    """
    Verifies the format of the user data specified: if some field is empty, if the password length is between 8 and 30,
    if there are blank spaces in the username and in the email, and if the passwords match.

    :param email: user's email
    :type email: str
    :param username: user's username
    :type username: str
    :param password: user's password
    :type password: str
    :param password_confirmation: confirmation of the user's password
    :type password_confirmation: str
    :param existing_user: if the operation that using the data is an update, this argument must be the user concerned
    :type existing_user: User

    :return: a tuple where the first value is a boolean indicating if the data is valid and the second value is an error message.
    """

    # Verifying if passwords match
    if password != password_confirmation:
        return "password", ERROR_NOT_CONFIRMED_PASSWORD

    try:
        EmailValidator().validate(email, user=existing_user)
    except ValidationError as e:
        return "email", e.message

    try:
        UsernameValidator().validate(username, user=existing_user)
    except ValidationError as e:
        return "username", e.message

    try:
        validate_password(password)
    except ValidationError as e:
        return "password", e.error_list[0].message

    return None, None