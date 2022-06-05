from django.contrib import messages
from django.contrib.auth.models import User


def is_valid_user_data_format(request, email, username, password, password_confirmation):
    '''Verifies the format of the user data specified: if some field is empty, if the password length is between 6 and 30, if there
    are blank spaces in the username and in the password, and if the passwords match.'''
    # Verifying if some field is empty
    if len(email) == 0 or len(username) == 0 or len(password) == 0:
        messages.error(request, "All fields are mandatory")
        print("Empty field")
        return False
    # Verifying length of the password
    elif len(password) < 6 or len(password) > 30:
        messages.error(request, "The password must have a length between 6 and 30")
        print("The password must have a length between 6 and 30")
        return False
    # Verifying if some field contains spaces
    elif username.find(" ") != -1 or password.find(" ") != -1:
        messages.error(request,"Username and password fields cannot contain spaces")
        print("Contain spaces")
        return False
    # Verifying if passwords match
    elif password != password_confirmation:
        messages.error(request, "Passwords no match")
        print("Passwords don't match")
        return False
    return True

def is_valid_new_user_info(request, email, username, password, password_confirmation):
    # Verifying the format of the infomation (email, username, password...)
    if not is_valid_user_data_format(request, email, username, password, password_confirmation):
        return False
    else:
        # Avoiding repeated emails for different users
        user_with_email = User.objects.filter(email = email)
        if len(user_with_email) > 0:
            messages.error(request, "This email is not available")
            print("Email not available")
            return False
        else:
            # Avoiding repeated usernames for different users 
            user_with_username = User.objects.filter(username = username)
            if len(user_with_username) > 0:
                messages.error(request, "This username is not available")
                print("Username not available")
                return False
    return True

def is_valid_updated_user_info(request, email, username, password, password_confirmation):
    # Verifying the format of the infomation (email, username, password...)
    if not is_valid_user_data_format(request, email, username, password, password_confirmation):
        return False
    else:
        # Avoiding repeated emails for different users
        user_with_email = User.objects.filter(email = email)
        # For an update of users currently logged in, it is allowed to use their current email
        is_email_of_current_user = request.user.is_authenticated and request.user.email == email
        if len(user_with_email) > 0 and not is_email_of_current_user:
            messages.error(request, "This email is not available")
            print("Email not available")
            return False
        else:
            # Avoiding repeated usernames for different users 
            user_with_username = User.objects.filter(username = username)
            # For an update of users currently logged in, it is allowed to use their current username
            is_username_of_current_user = request.user.is_authenticated and request.user.username == username
            if len(user_with_username) > 0 and not is_username_of_current_user:
                messages.error(request, "This username is not available")
                print("Username not available")
                return False
    return True