from django.db import models
from admin_app.models import Admin, Train

SERVICE_CHOICES = [
    ('reservation', 'Reservation'),
    ('business', 'Business'),
    ('economy', 'Economy'),
]

class Service(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='created_services')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('train', 'service_type')

    def __str__(self):
        return f"{self.train} - {self.service_type} - {self.price}"



