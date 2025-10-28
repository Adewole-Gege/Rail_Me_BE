from django.db import models
from admin_app.models import Train
from datetime import timedelta
from services_app.models import Service


# Create models here
TRAIN_DURATIONS = {
    'Rail-Me Express 001': 11,
    'Rail-Me Express 002': 9,
    'Rail-Me Express 003': 10,
    'Rail-Me Express 004': 11,
    'Rail-Me Express 005': 8,
    'Rail-Me Express 006': 11,
    'Rail-Me Express 007': 12,
    'Rail-Me Express 008': 11,
    'Rail-Me Express 009': 14,
    'Rail-Me Express 010': 11,
    'Rail-Me Express 020': 15,
    'Rail-Me Express 030': 12,
    'Rail-Me Express 040': 13,
    'Rail-Me Express 050': 15,
    'Rail-Me Express 060': 7,
    'Rail-Me Express 070': 8,
    'Rail-Me Express 080': 3,
    'Rail-Me Express 090': 8,
    'Rail-Me Express 101': 6,
    'Rail-Me Express 202': 9,
}


SERVICE_CHOICES = [
        ('reservation', 'Reservation'),
        ('economy', 'Economy'),
        ('business', 'Business'),
    ]


class Booking(models.Model):
    user = models.ForeignKey('accounts_app.Passenger', on_delete=models.CASCADE, related_name='bookings')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='bookings')
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, default='reservation')
    seats_booked = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=81500.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    booked_at = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        # Get price per seat from Service
        service_obj = Service.objects.filter(train=self.train, service_type=self.service).first()
        if service_obj:
            self.price = service_obj.price
        else:
            # fallback to reservation
            reservation = Service.objects.filter(train=self.train, service_type='reservation').first()
            if reservation:
                self.price = reservation.price

        # Calculate total price automatically
        self.total_price = self.price * self.seats_booked

        # Automatically calculate arrival time
        if not self.arrival_time and self.train:
            duration_hours = TRAIN_DURATIONS.get(self.train.train_name, 10)
            self.arrival_time = self.departure_time + timedelta(hours=duration_hours)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} booked {self.train.train_name} ({self.service}) for {self.total_price}"
    
    
