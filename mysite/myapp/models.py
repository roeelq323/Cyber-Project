from django.db import models,connection
import secrets
import hashlib
from .password_config import MAX_HISTORY

# Create your models here.

# SITE USERS MODEL
class MyappUsers(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=16)
    email = models.CharField(max_length=256)
    salt = models.CharField(max_length=32)
    for x in range(1, MAX_HISTORY+1): # creating password fields based on max history on the password config file
        field_name = f'password{x}'
        locals()[field_name] = models.CharField(max_length=200,default = '')
    history = models.IntegerField(default = 1) # saves the current password in ussage number
    last_login_attempt = models.DateTimeField(null=True, blank=True) # for buffer timer
    failed_login_attempts = models.IntegerField(default=0) # for counting login attempts 

# making djnago create a table in the database when doing migrations
    class Meta:
        managed=True
        db_table = 'site_users'


    @staticmethod
    def hash_password(password, salt):
        # Concatenate the password and salt and hash using a secure hashing algorithm (e.g., SHA-256)
        password_salt = password + salt
        hashed_password = hashlib.sha256(password_salt.encode()).hexdigest()
        return hashed_password

    def set_password(self, password):
        self.salt = secrets.token_hex(16)
        # Hash the password with the salt
        self.password1 = self.hash_password(password, self.salt)
    
    def change_password(self, password):
       setattr(self,f'password{self.history+1}',self.hash_password(password, self.salt))

    def check_password(self, password):
        # Check if the provided password matches the stored password
        hashed_password = self.hash_password(password, self.salt)
        return self.password == hashed_password


# CUSTOMERS MODEL
class Customers(models.Model):
    customer_id = models.CharField(max_length=9,primary_key=True)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=256)
    email = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    card_type = models.CharField(max_length=50)

# making djnago create a table in the database when doing migrations
    class Meta:
        managed=True
        db_table = 'customers'


# getting all the customers data from the database
def customer_list_view():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM customers')
            customers = cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        customers = 'Some thing wrong please check your connection'

    return customers

# adding a customer to the database
def coorectAdd_customer(customer_data):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customers (`customer_id`, `first_name`, `last_name`, `email`, `phone_number`, `address`, `card_type`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [customer_data['customer_id'], customer_data['first_name'], customer_data['last_name'],
                 customer_data['email'], customer_data['phone_number'], customer_data['address'],
                 customer_data['card_type']]
            )
    except Exception as e:
        raise e