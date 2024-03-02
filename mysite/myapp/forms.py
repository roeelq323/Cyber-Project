"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import *
from django.forms import ModelForm
from django import forms
from .password_config import *
import string
import re



# EMAIL CREATION FORM
class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'Email'}))
    Code = forms.CharField(label=_("Code"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Code'}))


class EmailForm(ModelForm):
    email = forms.EmailField(label = "Email", required=True)

class Meta:
    exclude = ['created_at', 'edited at','message','subject']

    
# FORGOT PASSWORD FORM
class forgotPasswordForm(forms.Form):
    password = forms.CharField(label="Enter Password", max_length=40)
    password_repeat = forms.CharField(label="Repeat Password", max_length=40)
    
    def clean(self):
        cleaned_data = super().clean()
        self.check_passwords_match(cleaned_data)
        self.check_password_criteria(cleaned_data)
        return cleaned_data

    # function to check if the two passwords the user has entered match each other.
    def check_passwords_match(self, cleanedData):
        password = cleanedData.get("password")
        password_repeat = cleanedData.get("password_repeat")
        if password and password_repeat and password != password_repeat:
            print(
                "Passwords do not match. Please enter the same password in both fields.")
            self.add_error(
                'password_repeat', "Passwords do not match. Please enter the same password in both fields.")

    # function to check if the password the user has entered meets all the criteria from the password_config file
    def check_password_criteria(self, cleanedData):
        special_characters = set(string.punctuation)
        password = cleanedData.get("password")
        if not password:
            return
        else:
            # Check if the password meets the minimal length criteria
            if len(password) < MIN_PASSWORD_LENGTH:
                self.add_error(
                    'password', f'Password must contain at least {MIN_PASSWORD_LENGTH} characters.')
            # Check if the 'uppercase' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('uppercase'):
                if not any(char.isupper() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one uppercase letter.")
            #Check if the 'lowercase' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('lowercase'):
                if not any(char.islower() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one lowercase letter.")

            # Check if the 'number' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('number'):
                if not any(char.isdigit() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one number.")

            # Check if the 'special' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('special'):
                if not any(char in special_characters for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one special character.")
            # Check if the password appears in dictonary
            if password in PASSWORD_DICT:
                    self.add_error(
                        'password', "You can't pick this password")



# CHANGE PASSWORD FORM
class changePasswordForm(forms.Form):
    password_old = forms.CharField(label="Enter Your Old Password" , max_length=40)
    password = forms.CharField(label="Enter Password", max_length=40)
    password_repeat = forms.CharField(label="Repeat Password", max_length=40)
    
    def clean(self):
        cleaned_data = super().clean()
        self.check_passwords_match(cleaned_data)
        self.check_password_criteria(cleaned_data)
        return cleaned_data

    # function to check if the two passwords the user has entered match each other.
    def check_passwords_match(self, cleanedData):
        password = cleanedData.get("password")
        password_repeat = cleanedData.get("password_repeat")
        if password and password_repeat and password != password_repeat:
            print(
                "Passwords do not match. Please enter the same password in both fields.")
            self.add_error(
                'password_repeat', "Passwords do not match. Please enter the same password in both fields.")

    # function to check if the password the user has entered meets all the criteria from the password_config file
    def check_password_criteria(self, cleanedData):
        special_characters = set(string.punctuation)
        password = cleanedData.get("password")
        if not password:
            return
        else:
            # Check if the password meets the minimal length criteria
            if len(password) < MIN_PASSWORD_LENGTH:
                self.add_error(
                    'password', f'Password must contain at least {MIN_PASSWORD_LENGTH} characters.')
            # Check if the 'uppercase' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('uppercase'):
                if not any(char.isupper() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one uppercase letter.")
            #Check if the 'lowercase' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('lowercase'):
                if not any(char.islower() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one lowercase letter.")

            # Check if the 'number' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('number'):
                if not any(char.isdigit() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one number.")

            # Check if the 'special' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('special'):
                if not any(char in special_characters for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one special character.")
            # Check if the password appears in dictonary
            if password in PASSWORD_DICT:
                    self.add_error(
                        'password', "You can't pick this password")



class registrationForm(forms.Form):
    name = forms.CharField(label="Enter User Name", max_length=40, error_messages={
        "required": "This field cannot stay blank!",
        "max_length": "To many characters entered, maximum ammount is 40"
    })
    # Use EmailField for email validation
    email = forms.EmailField(label="Enter Email", max_length=254)
    password = forms.CharField(label="Enter Password", max_length=40)
    password_repeat = forms.CharField(
        label="Repeat Password", max_length=40)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not re.match(r'^.+@.+.com$', email):
            raise forms.ValidationError(
                "Please enter a valid email address ending with @example.com.")
        return email
    
#overriding clean method
    def clean(self):
        cleaned_data = super().clean()
        self.check_passwords_match(cleaned_data)
        self.check_password_criteria(cleaned_data)
        self.clean_email()
        return cleaned_data

    # function to check if the two passwords the user has entered match each other.
    def check_passwords_match(self, cleanedData):
        password = cleanedData.get("password")
        password_repeat = cleanedData.get("password_repeat")
        if password and password_repeat and password != password_repeat:
            print(
                "Passwords do not match. Please enter the same password in both fields.")
            self.add_error(
                'password_repeat', "Passwords do not match. Please enter the same password in both fields.")

    # function to check if the password the user has entered meets all the criteria from the password_config file
    def check_password_criteria(self, cleanedData):
        special_characters = set(string.punctuation)
        password = cleanedData.get("password")
        if not password:
            return
        else:
            # Check if the password meets the minimal length criteria
            if len(password) < MIN_PASSWORD_LENGTH:
                self.add_error(
                    'password', f'Password must contain at least {MIN_PASSWORD_LENGTH} characters.')
            # Check if the 'uppercase' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('uppercase'):
                if not any(char.isupper() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one uppercase letter.")
            #Check if the 'lowercase' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('lowercase'):
                if not any(char.islower() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one lowercase letter.")

            # Check if the 'number' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('number'):
                if not any(char.isdigit() for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one number.")

            # Check if the 'special' requirement is enabled
            if REQUIRED_CHARACTER_TYPES.get('special'):
                if not any(char in special_characters for char in password):
                    self.add_error(
                        'password', "Passwords must contain at least one special character.")
            # Check if the password appears in dictonary
            if password in PASSWORD_DICT:
                    self.add_error(
                        'password', "You can't pick this password")
                    

# CUSTOMER FORM
class CustomerForm(forms.Form):
    customer_ID = forms.CharField(max_length=9)
    print(customer_ID)
    customer_name = forms.CharField(label='customer-name', max_length=100)
    customer_Lastname = forms.CharField(label='customer-Lastname', max_length=100)
    customer_email = forms.EmailField()
    customer_phone = forms.CharField(max_length=20)
    customer_Address = forms.CharField(label='customer-Address', max_length=255)
    customer_Card_Type = forms.CharField(label='customer-Card_Type', max_length=50)

    def clean(self):
        cleaned_data = super().clean()

        for field_name, field_value in cleaned_data.items():
            if field_name == 'customer_ID':
                if '<' in str(field_value) and '>' in str(field_value) or len(field_name)!=9:
                    self.add_error(field_name, 'Invalid characters detected. HTML elements are not allowed.')
            else:
                if '<' in str(field_value) and '>' in str(field_value):
                    self.add_error(field_name, 'Invalid characters detected. HTML elements are not allowed.')
