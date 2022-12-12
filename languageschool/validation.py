from django.contrib.auth.models import User

ERROR_EMPTY_EMAIL = "Email field is mandatory"
ERROR_EMPTY_USERNAME = "Username field is mandatory"
ERROR_EMPTY_PASSWORD = "Password field is mandatory"
ERROR_LENGTH_PASSWORD = "The password must have a length between 8 and 30"
ERROR_LETTER_PASSWORD = "The password must have at least one letter"
ERROR_DIGIT_PASSWORD = "The password must have at least one digit"
ERROR_SPECIAL_CHARACTER_PASSWORD = "The password must have at least one special character"
ERROR_SPACE_IN_EMAIL = "Email field cannot contain spaces"
ERROR_SPACE_IN_USERNAME = "Username field cannot contain spaces"
ERROR_NOT_CONFIRMED_PASSWORD = "Passwords do not match"
ERROR_NOT_AVAILABLE_EMAIL = "This email is not available"
ERROR_NOT_AVAILABLE_USERNAME = "This username is not available"


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
    # Verifying if some field is empty
    if (email is None) or (len(email) == 0):
        return "email", ERROR_EMPTY_EMAIL

    if (username is None) or (len(username) == 0):
        return "username", ERROR_EMPTY_USERNAME

    if (password is None) or (len(password) == 0):
        return "password", ERROR_EMPTY_PASSWORD
    # Verifying length of the password
    if len(password) < 8 or len(password) > 30:
        return "password", ERROR_LENGTH_PASSWORD
    # Verifying if password contains required character types
    has_letter = False
    has_digit = False
    has_special_char = False

    for char in password:
        if char.isalpha():
            has_letter = True
        elif char.isdigit():
            has_digit = True
        else:
            has_special_char = True

        if has_letter and has_digit and has_special_char:
            break

    if not has_letter:
        return "password", ERROR_LETTER_PASSWORD

    if not has_digit:
        return "password", ERROR_DIGIT_PASSWORD

    if not has_special_char:
        return "password", ERROR_SPECIAL_CHARACTER_PASSWORD
    # Verifying if a field contains spaces
    if username.find(" ") != -1:
        return "username", ERROR_SPACE_IN_USERNAME

    if email.find(" ") != -1:
        return "email", ERROR_SPACE_IN_EMAIL
    # Verifying if passwords match
    if password != password_confirmation:
        return "password", ERROR_NOT_CONFIRMED_PASSWORD
    # Verifying if the specified email is available
    user_with_email = User.objects.filter(email=email).first()
    if ((existing_user is None) and (user_with_email is not None)) or \
            ((existing_user is not None) and (user_with_email is not None) and (user_with_email.id != existing_user.id)):
        return "email", ERROR_NOT_AVAILABLE_EMAIL
    # Verifying if the specified username is available
    user_with_username = User.objects.filter(username=username).first()
    if ((existing_user is None) and (user_with_username is not None)) or \
            ((existing_user is not None) and (user_with_username is not None) and (user_with_username.id != existing_user.id)):
        return "username", ERROR_NOT_AVAILABLE_USERNAME
    return None, None
