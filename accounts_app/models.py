from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
from datetime import timedelta
from django.utils import timezone


# Create your models here.
class PassengerManager(BaseUserManager):
    def create_user(self, email, phone_number, first_name, last_name, password=None):
        if not email:
            raise ValueError("Email is required")
        if not phone_number:
            raise ValueError("Phone number is required")
        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")
        if not password:
            raise ValueError("Please provide a password")

        email = self.normalize_email(email)
        passenger = self.model(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        )
        passenger.set_password(password)
        passenger.save(using=self._db)
        return passenger

    def create_superuser(self, email, phone_number, first_name, last_name, password=None):
        passenger = self.create_passenger(email, phone_number, first_name, last_name, password)
        passenger.is_staff = True
        passenger.is_superuser = True
        passenger.save(using=self._db)
        return passenger
    
    
class Passenger(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  # New field to track verification status

    objects = PassengerManager() # tells django not to use the default user manager (objects) but to use the custom PassengerManager instead
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name'] # Since email is set to 
    # USERNAME_FIELD you don't need to add it here
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}" # this returns the string representation of the Passenger instance which is the first name and last name concatenated together
    
    
class OTP(models.Model):
    target = models.CharField(max_length=255)  # email or phone
    purpose = models.CharField(max_length=8, null=True, blank=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self): # this method returns a string representation of the OTP instance
        return f"{self.target} - {self.code}"

    def is_valid(self):
        return timezone.now() < self.expires_at and not self.is_used # checks if the OTP is still valid (not expired and not used)
    
    
def generate_otp(target, purpose=None, expiry_minutes=5):
    code = str(random.randint(100000, 999999))
    expires_at = timezone.now() + timedelta(minutes=int(expiry_minutes)) # sets the expiration time by adding the expiry duration to the current time
    OTP.objects.filter(target=target, is_used=False, expires_at__lt=timezone.now()).delete() # deletes old OTPs for this target that haven’t been used but already expired
    OTP.objects.create( # saves the new OTP in the database with its target, code, purpose, and expiration time
        target=target,
        code=code,
        purpose=purpose,
        expires_at=expires_at
    )

    return code # returns the generated OTP code so it can be sent to the user via email or SMS

