from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone
from django.conf import settings


# ------------------------ CustomUser Model ------------------------
class CustomUser(AbstractUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('user', 'ผู้ใช้งานทั่วไป'),
        ('admin', 'ผู้ดูแลระบบ'),
        ('manager', 'เจ้าของลานจอดรถ'),
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


# ------------------------ Parking Location Model ------------------------
class ParkingLocation(models.Model):
    id = models.BigAutoField(primary_key=True)  # ใช้ BigAutoField แทน bigint
    name = models.CharField(max_length=100)  # ชื่อสถานที่
    slug = models.SlugField(max_length=50, unique=True)  # slug สำหรับ URL
    description = models.TextField(null=True, blank=True)  # รายละเอียด (สามารถว่างได้)
    total_spots = models.IntegerField(default=0)  # จำนวนช่องจอดทั้งหมด
    camera_url = models.URLField(null=True, blank=True)
    available_spots = models.IntegerField(default=0)  # จำนวนช่องจอดที่ว่าง
    created_at = models.DateTimeField(auto_now_add=True)  # เวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # เวลาที่อัปเดตล่าสุด
    image = models.ImageField(upload_to='parking_images/', null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ใช้ settings.AUTH_USER_MODEL แทน auth.User
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


# ------------------------ Parking Spot Model ------------------------
class ParkingSpot(models.Model):
    spot_number = models.IntegerField()
    is_available = models.BooleanField(default=True)
    location = models.ForeignKey(ParkingLocation, on_delete=models.CASCADE)
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    x_position = models.IntegerField(default=100, null=True, blank=True)  # ความกว้าง
    y_position = models.IntegerField(default=100, null=True, blank=True)  # ความยาว
    width = models.IntegerField(default=100, null=True, blank=True)  # ความกว้าง
    height = models.IntegerField(default=100, null=True, blank=True)  # ความยาว
    def __str__(self):
        return f"Spot {self.spot_number} at {self.location.name}"


# ------------------------ Booking Model (การจองปัจจุบัน) ------------------------

from django.db import models
from django.utils import timezone
from django.conf import settings

class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),      # กำลังใช้งาน
        ('cancelled', 'Cancelled'), # ถูกยกเลิก
        ('completed', 'Completed') # เสร็จสิ้น
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    location = models.ForeignKey(ParkingLocation, on_delete=models.CASCADE)
    reservation_date = models.DateField(default=timezone.now)
    reservation_start_time = models.TimeField(default="08:00:00")
    reservation_end_time = models.TimeField(default="12:00:00")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    cancelled_at = models.DateTimeField(null=True, blank=True)  # เวลาที่ยกเลิก (ถ้ามี)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """ อัปเดตสถานะของที่จอดเมื่อมีการจอง """
        if self.status == 'active':
            self.parking_spot.is_available = False
            self.parking_spot.reserved_by = self.user
        elif self.status in ['cancelled', 'completed']:
            self.parking_spot.is_available = True
            self.parking_spot.reserved_by = None
        self.parking_spot.save()  # บันทึกการเปลี่ยนแปลงของ ParkingSpot
        super().save(*args, **kwargs)  # บันทึกการจอง

    def complete_booking(self):
        """ ย้ายข้อมูลจาก Booking ไป Reservation และคืนที่จอด """
        if self.status == 'active':  # ตรวจสอบว่าการจองยังไม่ถูกยกเลิก
            Reservation.objects.create(
                user=self.user,
                parking_spot=self.parking_spot,
                location=self.location,
                reservation_date=self.reservation_date,
                reservation_start_time=self.reservation_start_time,
                reservation_end_time=self.reservation_end_time,
                completed_at=timezone.now()
            )
            self.status = 'completed'
            self.save()

    def cancel_booking(self):
        """ ให้ผู้ใช้หรือ Manager สามารถยกเลิกการจองได้ และคืนที่จอด """
        if self.status == 'active':
            self.status = 'cancelled'
            self.cancelled_at = timezone.now()
            self.save()

    def __str__(self):
        return f"Booking by {self.user.username} ({self.status}) on {self.reservation_date}"





# ------------------------ Reservation Model (เก็บประวัติการจอง) ------------------------
class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    location = models.ForeignKey(ParkingLocation, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    reservation_start_time = models.TimeField()
    reservation_end_time = models.TimeField()
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation (Completed) by {self.user.username} on {self.reservation_date}"
