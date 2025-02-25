import cv2
import torch
from django.apps import apps
from .utils import update_parking_status  # ฟังก์ชันสำหรับอัปเดตสถานะ
import threading

def load_model():
    """
    โหลดโมเดล YOLOv5
    """
    try:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        return model
    except Exception as e:
        print(f"Error loading YOLOv5 model: {e}")
        return None

def get_camera_url(location_name):
    """
    ดึง URL ของกล้องสำหรับ Location ที่เลือก
    """
    ParkingLocation = apps.get_model('easypark', 'ParkingLocation')
    try:
        location = ParkingLocation.objects.get(name=location_name)
        return location.camera_url
    except ParkingLocation.DoesNotExist:
        print(f"Location {location_name} does not exist.")
        return None
    except Exception as e:
        print(f"Error retrieving camera URL: {e}")
        return None

def get_rois_from_db(location_name):
    """
    ดึง ROIs จากฐานข้อมูลตามสถานที่ที่เลือก
    """
    ROI = apps.get_model('easypark', 'ROI')
    ParkingLocation = apps.get_model('easypark', 'ParkingLocation')

    try:
        location = ParkingLocation.objects.get(name=location_name)
        rois = ROI.objects.filter(location=location)
        return [(roi.parking_spot.spot_number, roi.x_position, roi.y_position, roi.width, roi.height) for roi in rois]
    except ParkingLocation.DoesNotExist:
        print(f"Location '{location_name}' does not exist.")
        return []
    except Exception as e:
        print(f"Error retrieving ROIs: {e}")
        return []

def start_detection_in_background(selected_location):
    """
    เริ่มการตรวจจับใน Background Thread
    """
    thread = threading.Thread(target=detect_cars, args=(selected_location,), daemon=True)
    thread.start()

def detect_cars(selected_location):
    """
    ตรวจจับรถยนต์ใน Location ที่เลือก และอัปเดตสถานะในฐานข้อมูล
    """
    model = load_model()
    if not model:
        print("Model loading failed. Aborting detection.")
        return

    camera_url = get_camera_url(selected_location)
    if not camera_url:
        print(f"Cannot find camera URL for location: {selected_location}")
        return

    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot connect to camera for location: {selected_location}")
        return

    current_rois = get_rois_from_db(selected_location)
    if not current_rois:
        print(f"No ROIs defined for location: {selected_location}")
        return

    print(f"Starting detection for location: {selected_location}")

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                print(f"Cannot read frames from camera for location: {selected_location}")
                break

            results = model(frame)
            detections = results.pandas().xyxy[0]  # ดึงข้อมูล bounding boxes

            update_parking_status(current_rois, detections, selected_location)

        except Exception as e:
            print(f"Error during detection: {e}")
            break

        if cv2.waitKey(1000) & 0xFF == ord('q'):  # ทุก 1 วินาที
            break

    cap.release()
    cv2.destroyAllWindows()
