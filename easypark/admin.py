from django.contrib import admin
from .models import ParkingSpot

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('spot_number', 'is_available', 'license_plate', 'reserved_by')  # เพิ่ม 'license_plate'
    list_editable = ('is_available', 'license_plate')  # เพิ่ม 'license_plate'
    search_fields = ('spot_number', 'license_plate')
    list_filter = ('is_available',)

    # ฟังก์ชันสำหรับ action กำหนดเอง
    actions = ['mark_as_available', 'mark_as_unavailable']

    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_as_available.short_description = "เปลี่ยนสถานะเป็นว่าง"

    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = "เปลี่ยนสถานะเป็นไม่ว่าง"
