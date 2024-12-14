from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


from django.contrib.auth.models import AbstractUser,PermissionsMixin
from django.db import models

class CustomUser(AbstractUser,PermissionsMixin):
    ROLE_CHOICES = [
        ('user', 'ผู้ใช้งานทั่วไป'),
        ('admin', 'ผู้ดูแลระบบ'),
        ('manager', 'เจ้าของร้าน/สถานที่'),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
    )

    def is_manager(self):
        return self.role == 'manager'

    def is_admin(self):
        return self.role == 'admin'



class ParkingLocation(models.Model):
    id = models.BigAutoField(primary_key=True)  # ใช้ BigAutoField แทน bigint
    name = models.CharField(max_length=100)  # ชื่อสถานที่
    slug = models.SlugField(max_length=50, unique=True)  # slug สำหรับ URL
    description = models.TextField(null=True, blank=True)  # รายละเอียด (สามารถว่างได้)
    total_spots = models.IntegerField(default=0)  # จำนวนช่องจอดทั้งหมด
    available_spots = models.IntegerField(default=0)  # จำนวนช่องจอดที่ว่าง
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # เวลาที่อัปเดตล่าสุด

    def __str__(self):
        return self.name


class ParkingSpot(models.Model):
    spot_number = models.IntegerField()  # หมายเลขช่องจอด
    is_available = models.BooleanField(default=True)  # สถานะช่องจอด
    date = models.DateField(null=True, blank=True)  # วันที่ใช้งาน (ถ้ามี)
    license_plate = models.CharField(max_length=20, null=True, blank=True)  # ทะเบียนรถ (ถ้ามี)
    location = models.ForeignKey(ParkingLocation, on_delete=models.CASCADE)  # ForeignKey ไปยังสถานที่
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ใช้ settings.AUTH_USER_MODEL แทน auth.User
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )  # ผู้จอง
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # เวลาที่แก้ไขล่าสุด

    def __str__(self):
        return f"Spot {self.spot_number} at {self.location.name}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ใช้ settings.AUTH_USER_MODEL แทน auth.User
        on_delete=models.CASCADE
    )  # ผู้ใช้ที่จอง
    parking_spot = models.ForeignKey(
        ParkingSpot, on_delete=models.CASCADE
    )  # ช่องที่จอด (ForeignKey)
    reservation_date = models.DateField()  # วันที่จอง
    location = models.ForeignKey(
        ParkingLocation, on_delete=models.CASCADE
    )  # สถานที่
    reservation_start_time = models.TimeField(default='08:00:00')  # เวลาเริ่มต้น
    reservation_end_time = models.TimeField(default='12:00:00')  # เวลาสิ้นสุด
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='active'
    )  # สถานะการจอง
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # เวลาที่แก้ไขล่าสุด

    def __str__(self):
        return f"Reservation by {self.user.username} on {self.reservation_date} ({self.reservation_start_time} - {self.reservation_end_time})"





    









    


