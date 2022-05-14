from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from languageschool.models import Score
from languageschool.views.general import request_contains
from django.contrib.auth.hashers import make_password

def sign_in(request):
    return render(request, 'account/sign_in.html')

def is_valid_user_date_format(request, email, username, password, password_confirmation):
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
    if not is_valid_user_date_format(request, email, username, password, password_confirmation):
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
    if not is_valid_user_date_format(request, email, username, password, password_confirmation):
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

def create_user(request):
    if request.method == "POST":
        if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
            email = request.POST["email"]
            username = request.POST["username"]
            password = request.POST["password"]
            password_confirmation = request.POST["password_confirmation"]
            if is_valid_new_user_info(request, email, username, password, password_confirmation):
                user = User.objects.create_user(username=username, email=email,password=password)
                user.save()
                messages.success(request, "User sucessfully created")
                print("User created")

                return redirect('account_sign_in')
    return sign_in(request)

def login(request):
    return render(request, 'account/login.html')

def auth_user(request):
    if request.method == "POST":
        if request_contains(request.POST, ["username", "password"]):
            username = request.POST["username"].strip()
            password = request.POST["password"].strip()

            user = auth.authenticate(request, username = username, password = password)

            if user is not None:
                auth.login(request, user)
                return redirect('index')
            else:
                messages.error(request,"Incorrect username or password")
    return login(request)

def logout(request):
    auth.logout(request)
    return redirect('index')

def profile(request):
    scores = []
    if request.user.is_authenticated:
        scores = Score.objects.filter(user = request.user).order_by('language')
    return render(request, 'account/profile.html', {'scores': scores})

def update_user(request):
    # Users are allowed to update a user info only if they are authenticated in their account.
    if request.user.is_authenticated:
        return render(request, 'account/update_user.html', {'user_id' : request.user.id})
    # If the user is not logged, redirect to the index page
    return redirect('index')

def do_update_user(request):
    if request.method == "POST" and request.user.is_authenticated:
        if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]): 
            email = request.POST["email"]
            username = request.POST["username"]
            password = request.POST["password"]
            password_confirmation = request.POST["password_confirmation"]
            if is_valid_updated_user_info(request, email, username, password, password_confirmation):
                # Update information of the user currently logged in
                request.user.email = email
                request.user.username = username
                request.user.password = make_password(password)
                request.user.save()
                # Login of the user with the new information(if it is not done, the user is automatically logged out)
                user = auth.authenticate(request, username = username, password = password)
                auth.login(request, user)
                return redirect('account_profile')
    return update_user(request)

def delete_user(request):
    # It is important to be sure that the method was POST in order to avoid users to accidentally delete their accounts by merely accessing this endpoint
    if request.method == "POST":
        if request.user.is_authenticated:
            request.user.delete()
    return redirect('index')