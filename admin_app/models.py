from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import random
from datetime import timedelta
from django.utils import timezone


class AdminManager(BaseUserManager):
    def create_user(self, email, phone_number, first_name, last_name, password=None):
        if not email:
            raise ValueError("Admin must have an email")
        
        email = self.normalize_email(email)
        admin = self.model(
            email=email,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
        )
        admin.set_password(password)
        admin.save(using=self._db)
        return admin

    def create_superuser(self, email, phone_number, first_name, last_name, password=None):
        admin = self.create_user(email, phone_number, first_name, last_name, password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save(using=self._db)
        return admin


class Admin(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name']

    # Avoid clashes with Passenger
    groups = models.ManyToManyField('auth.Group', related_name='admin_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='admin_permissions_set', blank=True)

    objects = AdminManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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

    return code


STATION_CHOICES = [
    ('Abeokuta Central', 'Abeokuta Central'),
    ('Katsina Station', 'Katsina Station'),
    ('Jigawa Station', 'Jigawa Station'),
    ('Abuja Idu Station', 'Abuja Idu Station'),
    ('Kano Station', 'Kano Station'),
    ('Kaduna Station', 'Kaduna Station'),
    ('Kebbi Station', 'Kebbi Station'),
    ('Sokoto Station', 'Sokoto Station'),
    ('Zamfara Station', 'Zamfara Station'),
    ('Adamawa Station', 'Adamawa Station'),
    ('Bauchi Station', 'Bauchi Station'),
    ('Borno Station', 'Borno Station'),
    ('Gombe Station', 'Gombe Station'),
    ('Taraba Terminal', 'Taraba Terminal'),
    ('Yobe Station', 'Yobe Station'),
    ('Kogi Terminus', 'Kogi Terminus'),
    ('Benue Station', 'Benue Station'),
    ('Kwara Station', 'Kwara Station'),
    ('Nasarawa Station', 'Nasarawa Station'),
    ('Niger Station', 'Niger Station'),
    ('Plateau Station', 'Plateau Station'),
]

TRAIN_NAME_CHOICES = [
    ('Rail-Me Express 001', 'Rail-Me Express 001 (Abeokuta to Katsina)'),
    ('Rail-Me Express 002', 'Rail-Me Express 002 (Abeokuta to Kaduna)'),
    ('Rail-Me Express 003', 'Rail-Me Express 003 (Abeokuta to Kano)'),
    ('Rail-Me Express 004', 'Rail-Me Express 004 (Abeokuta to Jigawa)'),
    ('Rail-Me Express 005', 'Rail-Me Express 005 (Abeokuta to Abuja)'),
    ('Rail-Me Express 006', 'Rail-Me Express 006 (Abeokuta to Kebbi)'),
    ('Rail-Me Express 007', 'Rail-Me Express 007 (Abeokuta to Sokoto)'),
    ('Rail-Me Express 008', 'Rail-Me Express 008 (Abeokuta to Zamfara)'),
    ('Rail-Me Express 009', 'Rail-Me Express 009 (Abeokuta to Adamawa)'),
    ('Rail-Me Express 010', 'Rail-Me Express 010 (Abeokuta to Bauchi)'),
    ('Rail-Me Express 020', 'Rail-Me Express 020 (Abeokuta to Borno)'),
    ('Rail-Me Express 030', 'Rail-Me Express 030 (Abeokuta to Gombe)'),
    ('Rail-Me Express 040', 'Rail-Me Express 040 (Abeokuta to Taraba)'),
    ('Rail-Me Express 050', 'Rail-Me Express 050 (Abeokuta to Yobe)'),
    ('Rail-Me Express 060', 'Rail-Me Express 060 (Abeokuta to Kogi)'),
    ('Rail-Me Express 070', 'Rail-Me Express 070 (Abeokuta to Benue)'),
    ('Rail-Me Express 080', 'Rail-Me Express 080 (Abeokuta to Kwara)'),
    ('Rail-Me Express 090', 'Rail-Me Express 090 (Abeokuta to Nasarawa)'),
    ('Rail-Me Express 101', 'Rail-Me Express 101 (Abeokuta to Niger)'),
    ('Rail-Me Express 202', 'Rail-Me Express 202 (Abeokuta to Plateau)'),
]


class Train(models.Model):
    name = models.CharField(max_length=100, choices=TRAIN_NAME_CHOICES)
    departure_station = models.CharField(max_length=100, choices=STATION_CHOICES)
    destination = models.CharField(max_length=100)
    arrival_station = models.CharField(max_length=100, choices=STATION_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.BinaryField()
    
    total_seats = models.IntegerField(default=100)
    seats_remaining = models.IntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('name', 'departure_station', 'destination')
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.seats_remaining = self.total_seats

        super().save(*args, **kwargs)
             
    def __str__(self):
        return f"{self.name} ({self.departure_station} to {self.destination})"

