# easypark/video_stream.py

import cv2
import torch
import threading
from easypark.models import ParkingLocation
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse

# โหลดโมเดล YOLOv5
def load_model():
    try:
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
        return model
    except Exception as e:
        print(f"Error loading YOLOv5 model: {e}")
        return None

model = load_model()

# ROIs ของแต่ละสถานที่  # x y  width height
rois = {
    "อ้อมใหญ่": [(50, 480, 150, 150),(530, 260, 150, 150),(750, 200, 120, 120)],
    "วงเวียนอุบล": [(200, 430, 150, 150), (80, 200, 150, 150)],
    "วงเวียนร้อยเอ็ด": [(400, 400, 200, 200),(700, 200, 200, 200),(1000, 200, 200, 200)],
    "อาคารศิลปะศาสตร์": [(300, 300, 200, 200), (600, 200, 200, 200)],
    "ตึกเภสัช": [(400, 400, 200, 200),(700, 200, 200, 200),(1000, 200, 200, 200)],
    "locaiontest": [(400, 400, 200, 200),(700, 200, 200, 200),(1000, 200, 200, 200)],
}

def generate_frames(camera_url, location_name):  # ✅ ต้องมีทั้ง 2 argument
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot connect to camera: {camera_url}")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break

        # ตรวจจับวัตถุ
        results = model(frame)
        detections = results.pandas().xyxy[0]

        # วาด ROIs
        # วาด ROIs และเพิ่มข้อความ
        for idx, (x, y, w, h) in enumerate(rois.get(location_name, [])):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Spot {idx+1}", (x, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)


        # วาด bounding box ของรถที่ตรวจจับได้
        for _, row in detections.iterrows():
            x1, y1, x2, y2, conf, cls = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax']), row['confidence'], row['name']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"{cls} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
