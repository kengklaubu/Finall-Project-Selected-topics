from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ParkingSpot(models.Model):
    spot_number = models.IntegerField()
    is_available = models.BooleanField(default=True)
    reserved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)  # กำหนด default ให้เป็นวันที่ปัจจุบัน
    location = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=20, blank=True, null=True)



    def __str__(self):
        return f'ช่องจอด {self.spot_number}'


    


