from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

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
            if len(email) == 0:
                messages.error(request, "Email cannot be empty")
                print("Empty email")
            elif len(username) == 0:
                messages.error(request, "Username cannot be empty")
                print("Empty username")
            elif password != password_confirmation:
                messages.error(request, "Passwords no match")
                print("Passwords don't match")
            else:
                user_with_email = User.objects.filter(email = email)
                if len(user_with_email) > 0:
                    messages.error(request, "This email is not available")
                    print("Email not available")
                else: 
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
            