from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from languageschool.views.general import request_contains

def sign_in(request):
    return render(request, 'account/sign_in.html')

def create_user(request):
    if request.method == "POST":
        if request_contains(request.POST, ["email", "username", "password", "password_confirmation"]):
            email = request.POST["email"]
            username = request.POST["username"]
            password = request.POST["password"]
            password_confirmation = request.POST["password_confirmation"]
            # Verifying if some field is empty
            if len(email) == 0 or len(username) == 0 or len(password) == 0:
                messages.error(request, "All fields are mandatory")
                print("Empty field")
            # Verifying length of the password
            elif len(password) < 6 or len(password) > 30:
                messages.error(request, "The password must have a length between 6 and 30")
                print("The password must have a length between 6 and 30")
            # Verifying if some field contains spaces
            elif username.find(" ") != -1 or password.find(" ") != -1:
                messages.error(request,"Username and password fields cannot contain spaces")
                print("Contain spaces")
            # Verifying if passwords match
            elif password != password_confirmation:
                messages.error(request, "Passwords no match")
                print("Passwords don't match")
            else:
                # Avoiding repeated emails for different users
                user_with_email = User.objects.filter(email = email)
                if len(user_with_email) > 0:
                    messages.error(request, "This email is not available")
                    print("Email not available")
                else:
                    # Avoiding repeated usernames for different users 
                    user_with_username = User.objects.filter(username = username)
                    if len(user_with_username) > 0:
                        messages.error(request, "This username is not available")
                        print("Username not available")
                    else:
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