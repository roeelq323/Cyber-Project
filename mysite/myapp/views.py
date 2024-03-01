from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse
from myapp.models import *
from django.db import connection
from contextlib import _RedirectStream
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
import random
import pyotp
import hashlib
from django.shortcuts import render, redirect
from django.db import connection
from .forms import *
import secrets
import hashlib
from django.utils import timezone


def login_view(request):
    if request.method == 'POST':
        #getting the fields from the user
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == '' or password == '':
            error_message = f"Not all fields are filled"
            return render(request, 'login.html', {'error_message': error_message})

        try:
            user = MyappUsers.objects.get(username=username)
        except MyappUsers.DoesNotExist:
            error_message = f"User Not Found!"
            return render(request, 'login.html', {'error_message': error_message})

        cooldown_time = timezone.now() - timezone.timedelta(minutes=2)  # 3 minute cooldown
        if user.last_login_attempt and user.last_login_attempt > cooldown_time:
            time_remaining = user.last_login_attempt + timezone.timedelta(minutes=2) - timezone.now()
            error_message = f"Too many failed login attempts. Please try again after {time_remaining.seconds // 60} minutes."
            return render(request, 'login.html', {'error_message': error_message})

        num_pass = user.history
        stored_password = getattr(user, f'password{num_pass}')
        salt = user.salt
        hashed_password = hashlib.sha256((password + salt).encode()).hexdigest()

        if hashed_password == stored_password:
            request.session['username'] = username
            user.failed_login_attempts = 0  # Reset the failed attempts counter
            user.last_login_attempt = None  # Reset the cooldown
            user.save()
            return redirect('user')
        else:
            user.failed_login_attempts += 1
            user.save()

            if user.failed_login_attempts%3 == 0:
                user.last_login_attempt = timezone.now()
                user.save()
                error_message = f"Too many failed login attempts. Please try again after 2 minutes."
            else:
                error_message = f"Invalid login credentials for username '{username}'. Please try again."
            return render(request, 'login.html', {'error_message': error_message})
         
    return render(request, 'login.html')




 
        # with connection.cursor() as cursor:
        #     sql_query = "SELECT * FROM site_users WHERE username='" + username + "' AND password= '" + password + "' LIMIT 1"
        #     #sql_query = "SELECT * FROM myapp_users WHERE username=%s AND password=%s LIMIT 1" # SAFE
        #     cursor.execute(sql_query)
        #     #cursor.execute(sql_query, [username, password]) #SAFE
        #     user = cursor.fetchone()
            
        # if user:
        #    # login(request, user)
        #     return render(request, 'home.html', {'username': username})
        #     #return redirect('home')
    
        

def home(request):
   # if request.user.is_authenticated:
        return render(request, 'home.html')
        
   # else:
     #   return redirect('login')
 
     #------------------------FORGOT PASSWORD--------------------------------
def generate_otp_key():
    return pyotp.random_base32(length=32)  # Generate a 32-character base32 key (160 bits)




def generate_otp(user_hotp, counter):
    return user_hotp.at(counter)



def Send_code(email,otp):
    subject = 'Password Reset Code'
    message = f'Your password reset code is: {otp}'
    from_email = 'admin'
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)




def goto_forgot(request):
    if request.method == 'POST':
        if 'email' in request.POST:
            email = request.POST.get('email')
            if not MyappUsers.objects.filter(email=email).exists():
                messages.error(request, 'Email entered dosent exist')
            elif MyappUsers.objects.get(email = email).history == 3:
                messages.error(request, 'The user exceeded the number of password changes')
            else:
                data = (generate_otp_key()).encode('utf-8')
                hash_object = hashlib.sha1(data).hexdigest()
                request.session['hash_object'] = hash_object
                Send_code(email, hash_object)
                request.session['email'] = email
                return render(request, 'Confirm_code.html')
    return render(request, 'ForgotPage.html')



def Code_valid(request):
    if request.method == 'POST':
        if 'Code' in request.POST:
            input_code = request.POST.get('Code')
            Sha_code = request.session.get('hash_object')
            if input_code == Sha_code:
                del request.session['hash_object']
                return redirect('/forgotpassword')
            else:
                return render(request, 'Confirm_code.html', {'messeges':'Invalid code! Please try again.'})
    return render(request, 'Confirm_code.html')


def forgot_password(request):
    if request.method == "POST":
        form = forgotPasswordForm(request.POST)
        email = request.session.get('email')
        if form.is_valid():
            valid = True
            userPassword = form.cleaned_data["password"]
            user = MyappUsers.objects.get(email = email)
            new_password = hashlib.sha256((userPassword + user.salt).encode()).hexdigest()
            for x in range(1,user.history+1):
                old = getattr(user,f'password{x}')
                if new_password == old:
                    valid = False
                    break
            if valid == False:
                form.add_error('password', 'already used this password')
            else:
                user.change_password(userPassword)
                user.history+=1
                request.session['email'] = None
                user.save()
                print(form.cleaned_data)  # prints out the form dictionary
                return redirect("/")
    else:
        form = forgotPasswordForm()
    return render(request, "forgotpassword.html", {"form": form})



    # if request.method == 'POST':
    #     form = PasswordChangeForm(request.user, request.POST)
    #     if form.is_valid():
    #         form.save()
    #         messages.success(request, 'Your password was successfully updated!')
    #         return redirect('/')  # Redirect to homepage or login page
    #     else:
    #         messages.error(request, 'Please correct the error below.')
    # else:
    #     form = PasswordChangeForm(request.user)
    # return render(request, 'changepassword.html', {'form': form})


def change_password(request):
    if request.method == "POST":
        form = changePasswordForm(request.POST)
        username = request.session.get('username')
        if form.is_valid():
            valid = True
            userOld = form.cleaned_data["password_old"]
            userPassword = form.cleaned_data["password"]
            user = MyappUsers.objects.get(username = username)
            new_password = hashlib.sha256((userPassword + user.salt).encode()).hexdigest()
            curr_password = getattr(user,f'password{user.history}')     
            for x in range(1,user.history+1):
                old = getattr(user,f'password{x}')
                if new_password == old:
                    valid = False
                    break
            if user.history == 3:
                form.add_error('password_old', 'The user exceded the times he can change password!')
            elif  not hashlib.sha256((userOld + user.salt).encode()).hexdigest() == curr_password:
                form.add_error('password_old', 'incorrect old password')
            elif valid == False:
                form.add_error('password', 'already used this password')
            else:
                user.change_password(userPassword)
                user.history+=1
                request.session['email'] = None
                user.save()
                print(form.cleaned_data)  # prints out the form dictionary
                return redirect("/")
    else:
        form = changePasswordForm()
    return render(request, "changepassword.html", {"form": form})





def sign_up_vulnerable(request):
    if request.method == "POST":
        user_name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Construct the SQL query using string concatenation (vulnerable)
        query = "INSERT INTO login_screen_user (user_name, email, password) VALUES ('" + \
            user_name + "', '" + email + "', '" + password + "')"

        # Execute the SQL query
        with connection.cursor() as cursor:
            cursor.execute(query)

        return redirect("/")
    else:
        form = registrationForm()
    return render(request, "form_vulnerable.html", {"form": form})


def sign_up(request):
    if request.method == "POST":
        # passing request.POST generates a dict of values entered
        form = registrationForm(request.POST)
        if form.is_valid():
            userEmail = form.cleaned_data["email"]
            userPassword = form.cleaned_data["password"]
            userName = form.cleaned_data["name"]
            # check against database if email is already in use
            if MyappUsers.objects.filter(username=userName).exists():
                form.add_error(
                    'name', 'A user with this name already exists.')
            elif MyappUsers.objects.filter(email=userEmail).exists():
                form.add_error(
                    'email', 'A user with this email already exists.')
            elif userPassword:
                # Create a new User instance
                user = MyappUsers(username=userName, email=userEmail)
                # Set the password, which internally generates a salt and hashes the password
                user.set_password(userPassword)
                user.history = 1
                user.save()
                print(form.cleaned_data)  # prints out the form dictionary
                return redirect("/")
    else:
        form = registrationForm()
    return render(request, "form.html", {"form": form})





@never_cache
def index(request):
    try:
        customers = customer_list_view()
    except Exception as e:
        error_message = f"Error: {e}"
        return render(request, 'index.html', {'error_message': error_message})

    return render(request, 'index.html', {'customers': customers})

# def addCust(request):
#     return render(request, 'main/add_cust.html')
@never_cache
# def addCust(request):
#         if request.method == 'POST':
#             customer_data = {
#                 'customer_id': request.POST.get('customer-ID', ''),
#                 'first_name': request.POST.get('customer-name', ''),
#                 'last_name': request.POST.get('customer-Lastname', ''),
#                 'email': request.POST.get('customer-email', ''),
#                 'phone_number': request.POST.get('customer-phone', ''),
#                 'address': request.POST.get('customer-Address', ''),
#                 'card_type': request.POST.get('customer-Card_Type', ''),
#             }
#
#             try:
#                 add_customer(customer_data)
#             except Exception as e:
#                 error_message = f"Error: {e}"
#                 return render(request, 'main/index.html', {'error_message': error_message})
#
#         return render(request, 'main/add_cust.html')

@never_cache
def addCust(request):
    if request.method == 'POST':
        customer_data = {
            'customer_id': request.POST.get('customer-ID', ''),
            'first_name': request.POST.get('customer-name', ''),
            'last_name': request.POST.get('customer-Lastname', ''),
            'email': request.POST.get('customer-email', ''),
            'phone_number': request.POST.get('customer-phone', ''),
            'address': request.POST.get('customer-Address', ''),
            'card_type': request.POST.get('customer-Card_Type', ''),
        }
        special_characters = '"!@#$%^&*()''-+?_=,<>/"'
        letters = 'abcdefghijklmnopkrstuvqwxyz'
        numbers = '1234567890'

        if (any(c in special_characters for c in customer_data['customer_id']) or any(c in letters for c in customer_data['customer_id']) or
            any(c in special_characters for c in customer_data['first_name']) or any(c in numbers for c in customer_data['first_name']) or
            any(c in special_characters for c in customer_data['last_name']) or any(c in numbers for c in customer_data['last_name']) or
            any(c in special_characters for c in customer_data['phone_number']) or any(c in letters for c in customer_data['phone_number']) or
            any(c in special_characters for c in customer_data['address']) or
            any(c in special_characters for c in customer_data['card_type']) or any(c in numbers for c in customer_data['card_type'])): 
            error_message="One or more information that you gave was incorrect"
            return render(request, 'add_cust.html', {'error_message': error_message})
        try:
            #ex=add_customer(customer_data)
            coorectAdd_customer(customer_data)
        except Exception as e:
            # error_message = f"Error: {ex}"
            # print(ex)
            error_message="One or more information that you gave was incorrect "
            return render(request, 'add_cust.html', {'error_message': error_message})
        return redirect('user')
    return render(request, 'add_cust.html')
