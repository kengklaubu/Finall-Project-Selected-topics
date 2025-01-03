import os
from openpyxl import load_workbook
from django.conf import settings
from easypark.models import CustomUser, ParkingLocation, ParkingSpot, Reservation
from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    help = 'Load data from Excel into CustomUser, ParkingLocation, ParkingSpot, and Reservation models'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'easypark', 'fixtures', 'mockup-data.xlsx')

        # Load the Excel workbook
        wb = load_workbook(file_path)

        # Load CustomUser data
        user_sheet = wb['easypark_customuser']
        for row in user_sheet.iter_rows(min_row=2, values_only=True):
            user_id, username, email, first_name, last_name, password, is_staff, is_superuser = row

            user_instance, created = CustomUser.objects.get_or_create(
                id=user_id,
                defaults={
                    'username': username,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                }
            )
            if created:
                user_instance.set_password(password)
                user_instance.save()
                self.stdout.write(f"Created user: {username}")

        # Load ParkingLocation data
        location_sheet = wb['easypark_parkinglocation']
        for row in location_sheet.iter_rows(min_row=2, values_only=True):
            location_id, name, slug, description, total_spots, available_spots = row

            ParkingLocation.objects.get_or_create(
                id=location_id,
                defaults={
                    'name': name,
                    'slug': slug,
                    'description': description,
                    'total_spots': total_spots,
                    'available_spots': available_spots,
                }
            )

        # Load ParkingSpot data
        spot_sheet = wb['easypark_parkingspot']
        for row in spot_sheet.iter_rows(min_row=2, values_only=True):
            spot_id, spot_number, is_available, location_id = row

            location = ParkingLocation.objects.filter(id=location_id).first()
            if location:
                ParkingSpot.objects.get_or_create(
                    id=spot_id,
                    defaults={
                        'spot_number': spot_number,
                        'is_available': is_available,
                        'location': location,
                    }
                )

        # Load Reservation data
        reservation_sheet = wb['easypark_reservation']
        for row in reservation_sheet.iter_rows(min_row=2, values_only=True):
            reservation_id, user_id, parking_spot_id, reservation_date, start_time, end_time, status = row

            user = CustomUser.objects.filter(id=user_id).first()
            parking_spot = ParkingSpot.objects.filter(id=parking_spot_id).first()

            if user and parking_spot:
                try:
                    reservation_date = datetime.strptime(str(reservation_date), '%Y-%m-%d').date()
                except ValueError as e:
                    self.stdout.write(f"Invalid date format for reservation ID {reservation_id}. Skipping...")
                    continue

                Reservation.objects.get_or_create(
                    id=reservation_id,
                    defaults={
                        'user': user,
                        'parking_spot': parking_spot,
                        'reservation_date': reservation_date,
                        'reservation_start_time': start_time,
                        'reservation_end_time': end_time,
                        'status': status,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Data loaded successfully!"))
