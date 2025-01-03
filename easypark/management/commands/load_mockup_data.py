import os
import csv
from openpyxl import load_workbook  # ใช้สำหรับอ่านไฟล์ Excel
from django.core.management.base import BaseCommand
from django.conf import settings
from easypark.models import ParkingLocation, CustomUser, ParkingSpot

class Command(BaseCommand):
    help = 'Load mockup data from CSV and Excel files into ParkingLocation, CustomUser, and ParkingSpot models'

    def handle(self, *args, **options):
        # เส้นทางไฟล์
        csv_file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'data_10.csv')
        excel_file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'mockup-data.xlsx')

        # 1. อ่านข้อมูลจากไฟล์ CSV
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader, None)  # ข้าม header
                for row in reader:
                    location_name = row[0]  # สมมติว่า location_name อยู่ใน column แรกของ CSV

                    # สร้างหรืออัปเดตข้อมูล ParkingLocation
                    ParkingLocation.objects.get_or_create(
                        name=location_name,
                        defaults={"slug": location_name.replace(" ", "_").lower()}
                    )
                    self.stdout.write(f"Added location from CSV: {location_name}")
        else:
            self.stdout.write(self.style.ERROR(f"CSV file not found at {csv_file_path}"))

        # 2. อ่านข้อมูลจากไฟล์ Excel
        if os.path.exists(excel_file_path):
            wb = load_workbook(excel_file_path)
            sheet = wb.active  # ใช้แผ่นงานแรก
            for row in sheet.iter_rows(min_row=2, values_only=True):  # ข้าม header
                location_name, slug, other_field = row  # ปรับตามจำนวน column ใน Excel

                # สร้างหรืออัปเดตข้อมูล ParkingLocation
                ParkingLocation.objects.get_or_create(
                    name=location_name,
                    defaults={"slug": slug or location_name.replace(" ", "_").lower()}
                )
                self.stdout.write(f"Added location from Excel: {location_name}")
        else:
            self.stdout.write(self.style.ERROR(f"Excel file not found at {excel_file_path}"))

        self.stdout.write(self.style.SUCCESS("Data loading completed!"))
