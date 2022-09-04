from django.contrib.auth.models import User


def is_valid_user_data(email, username, password, password_confirmation, existing_user=None):
    """
    Verifies the format of the user data specified: if some field is empty, if the password length is between 6 and 30,
    if there are blank spaces in the username and in the password, and if the passwords match.

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
    if len(email) == 0 or len(username) == 0 or len(password) == 0:
        print("Empty field")
        return False, "All fields are mandatory"
    # Verifying length of the password
    if len(password) < 6 or len(password) > 30:
        print("The password must have a length between 6 and 30")
        return False, "The password must have a length between 6 and 30"
    # Verifying if some field contains spaces
    if username.find(" ") != -1 or password.find(" ") != -1:
        print("Contain spaces")
        return False, "Username and password fields cannot contain spaces"
    # Verifying if passwords match
    if password != password_confirmation:
        print("Passwords don't match")
        return False, "Passwords no match"
    # Verifying if the specified email is available
    user_with_email = User.objects.filter(email=email).first()
    if ((existing_user is None) and (user_with_email is not None)) or \
            ((existing_user is not None) and (user_with_email.id != existing_user.id)):
        print("Email not available")
        return False, "This email is not available"
    # Verifying if the specified username is available
    user_with_username = User.objects.filter(username=username).first()
    if ((existing_user is None) and (user_with_username is not None)) or \
            ((existing_user is not None) and (user_with_username.id != existing_user.id)):
        print("Username not available")
        return False, "This username is not available"
    return True, None
