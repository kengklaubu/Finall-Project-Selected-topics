from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ParkingSpot, Reservation, ParkingLocation

@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('spot_number', 'is_available', 'license_plate', 'reserved_by')
    list_editable = ('is_available', 'license_plate')
    search_fields = ('spot_number', 'license_plate')
    list_filter = ('is_available',)
    actions = ['mark_as_available', 'mark_as_unavailable']

    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)
    mark_as_available.short_description = "เปลี่ยนสถานะเป็นว่าง"

    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
    mark_as_unavailable.short_description = "เปลี่ยนสถานะเป็นไม่ว่าง"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'parking_spot', 'reservation_date', 'status']
    search_fields = ['user__username', 'parking_spot__spot_number']
    list_filter = ['status']


@admin.register(ParkingLocation)
class ParkingLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'total_spots', 'available_spots']
    search_fields = ['name']
    list_filter = ['total_spots', 'available_spots']


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

