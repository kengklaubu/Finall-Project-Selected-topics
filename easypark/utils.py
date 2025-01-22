from easypark.models import ParkingSpot
from django.apps import apps

def update_parking_status(rois, detections, location_name):
    ParkingSpot = apps.get_model('easypark', 'ParkingSpot')  # Lazy Load ParkingSpot
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
            parking_spot = ParkingSpot.objects.get(spot_number=spot_number, location__name=location_name)
            parking_spot.is_available = not detected
            parking_spot.save()
        except ParkingSpot.DoesNotExist:
            print(f"Parking spot {spot_number} in location {location_name} does not exist.")

