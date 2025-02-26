from django.apps import apps

def update_parking_status(rois, detections, location_name):
    """
    อัปเดตสถานะช่องจอดรถในฐานข้อมูล

    Args:
        rois (list): รายการของ ROI (spot_number, x, y, w, h)
        detections (DataFrame): Bounding boxes จาก YOLOv5
        location_name (str|int): ชื่อหรือ ID ของ Location ของช่องจอด
    """
    ParkingSpot = apps.get_model('easypark', 'ParkingSpot')  # Lazy Load ParkingSpot
    ParkingLocation = apps.get_model('easypark', 'ParkingLocation')  # Lazy Load ParkingLocation

    # ตรวจสอบว่า location_name เป็นตัวเลขหรือชื่อ
    try:
        if str(location_name).isdigit():  # ถ้าเป็นตัวเลขให้ใช้ ID
            location = ParkingLocation.objects.get(id=int(location_name))
        else:  # ถ้าเป็นชื่อให้ใช้ name
            location = ParkingLocation.objects.get(name=location_name)
    except ParkingLocation.DoesNotExist:
        print(f"❌ Location '{location_name}' does not exist.")
        return

    print(f"🔍 Updating parking status for location: {location.name} (ID {location.id})")

    for roi in rois:
        spot_number, x, y, w, h = roi
        detected = False

        for _, row in detections.iterrows():
            label = row['name']
            x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])

            if label == 'car' and (x1 < x + w and x2 > x and y1 < y + h and y2 > y):
                detected = True
                break

        try:
            parking_spot = ParkingSpot.objects.get(spot_number=spot_number, location=location)
            parking_spot.is_available = not detected
            parking_spot.save()
            print(f"✅ Updated spot {spot_number}: {'Available' if not detected else 'Occupied'}")
        except ParkingSpot.DoesNotExist:
            print(f"❌ Parking spot {spot_number} in location '{location.name}' does not exist.")
