import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from easypark.models import ParkingLocation, CustomUser, ParkingSpot  # อาจจะมีการนำเข้าโมเดลที่คุณต้องการเพิ่มข้อมูล

class Command(BaseCommand):
    help = 'Load mockup data from CSV file into ParkingLocation, CustomUser, and ParkingSpot models'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'static', 'easypark', 'data', 'data_10.csv')  # กำหนดเส้นทางไฟล์ CSV

        # อ่านข้อมูลจาก CSV
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # ข้าม header
                for row in reader:
                    location_name = row[0]  # สมมติว่า location_name อยู่ใน column แรกของ CSV

                    # สร้างหรืออัปเดตข้อมูล ParkingLocation
                    ParkingLocation.objects.get_or_create(
                        name=location_name,
                        defaults={"slug": location_name.replace(" ", "_").lower()}
                    )
                    self.stdout.write(f"Added location: {location_name}")
        else:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {file_path}"))
