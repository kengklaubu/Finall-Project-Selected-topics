import json
import requests
import csv
from django.shortcuts import render
import csv
import os
from django.conf import settings

def get_sheet_data():
    file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'parking_data.csv')  # ตัวอย่างที่เก็บไฟล์ใน static/data/
    
    data = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            data = list(reader)
    except FileNotFoundError:
        print("ไฟล์ CSV ไม่พบในโปรเจค")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
    
    return data

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user :
            print(user.role)  # เพิ่มบรรทัดนี้เพื่อเช็คว่า role ของผู้ใช้ถูกต้อง
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'manager':
                return redirect('manager_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            return render(request, 'easypark/login.html', {'error': 'Invalid login credentials'})

    return render(request, 'easypark/login.html')




from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login
from .models import CustomUser  

def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.set_password(form.cleaned_data['password'])  
            user.save()  
            login(request, user)  
            return redirect('homepage')  
    else:
        form = RegisterForm()
    
    return render(request, 'easypark/register.html', {'form': form})



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

# ฟังก์ชันนี้ใช้ตรวจสอบบทบาท
def is_admin(user):
    return user.role == 'admin'


# ฟังก์ชันนี้จะทำให้แค่แอดมินสามารถเข้าใช้งาน
from django.contrib.auth.decorators import login_required
from .models import CustomUser, ParkingLocation
@login_required
@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    users = CustomUser.objects.all()  # ดึงผู้ใช้ทั้งหมด
    total_users = users.count()  # นับจำนวนผู้ใช้ทั้งหมด
    locations = ParkingLocation.objects.all()
    total_locations = locations.count()

    context = {
        'users': users,
        'total_users': total_users,
        'total_locations': total_locations,
    }
    return render(request, 'easypark/admin_dashboard.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import ParkingLocation ,Reservation, ParkingSpot,Booking

@login_required
def manager_dashboard(request, location_id):
    # ค้นหา location ที่ผู้ใช้เป็นเจ้าของ
    location = ParkingLocation.objects.get(id=location_id)

    # ตรวจสอบว่า user เป็นเจ้าของ location นี้หรือไม่
    if location.owner != request.user:
        return HttpResponseForbidden("You do not have permission to access this location.")

    # ดึงข้อมูลที่ต้องการแสดงในหน้า dashboard
    reservations = Reservation.objects.filter(parking_spot__location=location)
    bookings = Booking.objects.filter(parking_spot__location=location)
    parking_spots = ParkingSpot.objects.filter(location=location)

    # ส่งข้อมูลทั้งหมดไปยัง template
    return render(request, 'easypark/manager_dashboard.html', {
        'location': location,
        'reservations': reservations,
        'parking_spots': parking_spots,
        'current_location': location.name,
        'bookings': bookings
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ParkingLocation
from .forms import ParkingLocationForm

@login_required
def manager_add_location(request):
    location = None  # กำหนดค่าเริ่มต้นให้ location เป็น None
    if request.method == "POST":
        form = ParkingLocationForm(request.POST, request.FILES)
        if form.is_valid():
            location = form.save(commit=False)
            location.owner = request.user
            location.save()
            messages.success(request, "✅ เพิ่มสถานที่จอดรถเรียบร้อยแล้ว!")

            return redirect('manager_dashboard', location.id)  # ✅ ใช้ location.id ที่เพิ่งบันทึก
    else:
        form = ParkingLocationForm()

    return render(request, 'easypark/manager_add_location.html', {
        'form': form,
        'location': location  # ✅ ส่ง location ไปที่ template
    })




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def update_parking_spot_position(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            spot_id = data.get("spot_id")
            x_position = data.get("x_position")
            y_position = data.get("y_position")

            spot = ParkingSpot.objects.get(id=spot_id)
            spot.x_position = x_position
            spot.y_position = y_position
            spot.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request method"})






@login_required
def cancel_reservation(request, reservation_id):
    # ตรวจสอบว่าเป็น Manager
    if request.user.role != 'manager':
        return redirect('homepage')

    try:
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.status = 'cancelled'  
        reservation.save()
        return redirect('manager_dashboard')  
    except Reservation.DoesNotExist:
        return redirect('manager_dashboard')  
    


from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import ParkingSpot

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import ParkingSpot

@login_required
def suspend_parking_spot(request, spot_id):
    # ตรวจสอบว่า user มีสิทธิ์เป็น 'manager'
    if request.user.role != 'manager':
        return JsonResponse({'success': False, 'message': 'Access Denied'}, status=403)

    try:
        # ดึงข้อมูลช่องจอดที่ตรงกับ spot_id
        parking_spot = ParkingSpot.objects.get(id=spot_id)

        # สลับสถานะความพร้อมใช้งานของช่องจอด
        parking_spot.is_available = not parking_spot.is_available
        parking_spot.save()

        # ส่งผลลัพธ์กลับในรูปแบบ JSON
        return JsonResponse({
            'success': True,
            'is_available': parking_spot.is_available
        })
    except ParkingSpot.DoesNotExist:
        # หากไม่พบช่องจอด
        return JsonResponse({'success': False, 'message': 'Parking spot not found'}, status=404)
    except Exception as e:
        # จัดการข้อผิดพลาดอื่น ๆ
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

    

    



from django.http import JsonResponse
from .models import ParkingLocation
from .detection_service import detect_cars  # ฟังก์ชันตรวจจับที่เชื่อมต่อกับกล้อง

def get_camera_url(location_name):
    try:
        location = ParkingLocation.objects.get(name=location_name)
        return location.camera_url
    except ParkingLocation.DoesNotExist:
        print(f"Location {location_name} does not exist.")
        return None



import time
from django.http import JsonResponse
from django.apps import apps
from .detection_service import start_detection_in_background

def start_detection(request):
    start_time = time.time()  # บันทึกเวลาที่เริ่ม
    location = request.GET.get('location')
    
    if not location:
        return JsonResponse({"error": "No location specified"}, status=400)

    app_config = apps.get_app_config('easypark')
    model = app_config.model  
    if model is None:
        return JsonResponse({"error": "Model not loaded"}, status=500)

    start_detection_in_background(location, model)

    end_time = time.time()  # บันทึกเวลาที่สิ้นสุด
    print(f"start_detection() took {end_time - start_time:.2f} seconds")

    return JsonResponse({"status": f"Detection started for location: {location}"})












from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import get_object_or_404
from .models import ParkingLocation
import cv2

def generate_raw_frames(camera_url):
    """
    สตรีมวิดีโอสดแบบปกติ (ไม่มี Bounding Box)
    """
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        print(f"Cannot connect to camera: {camera_url}")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def stream_video(request, location_id):
    """
    สตรีมวิดีโอสด (ไม่มี Bounding Box)
    """
    location = get_object_or_404(ParkingLocation, id=location_id)
    camera_url = location.camera_url

    return StreamingHttpResponse(
        generate_raw_frames(camera_url),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )



from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from easypark.models import ParkingLocation
from easypark.video_stream import generate_frames  # Import ฟังก์ชัน generate_frames

def video_feed(request, location_id):
    """
    สตรีมวิดีโอจากกล้องของสถานที่ที่เลือก
    """
    location = get_object_or_404(ParkingLocation, id=location_id)  # ดึงข้อมูลสถานที่
    camera_url = location.camera_url  # ดึง URL ของกล้อง

    if not camera_url:
        return StreamingHttpResponse(b'Error: Camera URL not found', content_type="text/plain")

    return StreamingHttpResponse(
        generate_frames(location),  # ✅ ส่งทั้ง `camera_url` และ `location.name`
        content_type="multipart/x-mixed-replace; boundary=frame"
    )











from django.http import JsonResponse
from .models import ParkingSpot

def get_parking_spots(request, location_id):
    parking_spots = ParkingSpot.objects.filter(location_id=location_id)

    spots_data = []
    for spot in parking_spots:
        reserved_by = spot.reserved_by.username if spot.reserved_by else 'None'
        license_plate = spot.license_plate if spot.license_plate else 'N/A'
        spots_data.append({
            'spot_number': spot.spot_number,
            'is_available': spot.is_available,
            'reserved_by': reserved_by,
            'license_plate': license_plate,
            'id': spot.id  # ทำให้มั่นใจว่า spot.id ถูกส่งมาด้วย
        })
    
    return JsonResponse({'parking_spots': spots_data})












from django.shortcuts import render, get_object_or_404
from .models import ParkingLocation

#def locations_page(request):
    #return render(request, 'easypark/locations.html')

def parking_location(request, location_slug):
    location = get_object_or_404(ParkingLocation, slug=location_slug)
    spots = location.parking_spots.all() 
    return render(request, 'easypark/parking_location.html', {'location': location, 'spots': spots})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reservation,Booking # นำเข้า Model ที่เก็บประวัติการจอง

@login_required
def profile(request):
    reservations = Reservation.objects.filter(user=request.user)  # ดึงประวัติการจองของผู้ใช้
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'easypark/profile.html', {'reservations': reservations,'bookings':bookings})

@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    return redirect('profile')


from django.shortcuts import render
from easypark.models import Reservation


def reservation_history(request):
    # ดึงประวัติการจอง
    reservations = Reservation.objects.select_related('location', 'parking_spot').filter(user=request.user)
    return render(request, 'easypark/reservation_history.html', {'reservations': reservations})


from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def view_reservation_history(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
    # Logic สำหรับผู้ดูแลระบบ


from django.shortcuts import render
from django.http import HttpResponseForbidden

def manage_parking_spots(request):
    if request.user.role != 'manager':
        return HttpResponseForbidden("คุณไม่มีสิทธิ์จัดการที่จอดรถ")
    # Logic สำหรับเจ้าของร้าน (สถานที่)
    return render(request, 'manage_parking_spots.html')




#ดึงข้อมูลทั้งหมด
#from django.shortcuts import render
#from .models import Reservation
#def reservation_history(request):
    # ตรวจสอบว่า Query ครบทุกข้อมูลในตาราง Reservation
    #reservations = Reservation.objects.select_related('location').all()
    #return render(request, 'reservation_history.html', {'reservations': reservations})





    
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login_page')

# easypark/views.py

from django.shortcuts import render

def password_reset(request):
    # แสดงหน้า password reset
    return render(request, 'easypark/password_reset1221.html')





from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import os
import csv
from django.conf import settings

def homepage(request):
    locations = ParkingLocation.objects.all()
    default_location = ParkingLocation.objects.get(name='อ้อมใหญ่')

    if request.user.is_authenticated:
        # ตรวจสอบ role ของผู้ใช้ที่ล็อกอิน
        if request.user.role == 'admin':
            return redirect('admin_dashboard')  # เปลี่ยนไปหน้าแดชบอร์ดของแอดมิน
        elif request.user.role == 'manager':
            # ตรวจสอบว่า manager เป็นเจ้าของ location อะไรบ้าง
            locations_owned_by_manager = ParkingLocation.objects.filter(owner=request.user)

            if locations_owned_by_manager.exists():
                # ถ้ามี location ที่เป็นของ manager ให้ redirect ไปที่หน้า dashboard ของ location แรก
                return redirect('manager_dashboard', location_id=locations_owned_by_manager.first().id)
            else:
                # ถ้า manager ไม่มี location ให้ไปที่หน้าอื่นหรือแสดงข้อมูล
                return render(request, 'easypark/home.html', {'locations': locations, 'default_location': default_location, 'message': 'You do not own any locations.'})
        else:
            # สำหรับผู้ใช้ทั่วไป
            return render(request, 'easypark/home.html', {'locations': locations, 'default_location': default_location})
    else:
        # ถ้าผู้ใช้ไม่ได้ล็อกอิน ก็ให้แสดงหน้า homepage
        return render(request, 'easypark/home.html', {'locations': locations, 'default_location': default_location})


    








from django.http import JsonResponse
from .models import ParkingSpot

def get_parking_status(request):
    # ดึง location_id จาก request
    location_id = request.GET.get('location_id')

    # ตรวจสอบว่า location_id ถูกส่งมาหรือไม่
    if not location_id:
        return JsonResponse({'error': 'กรุณาระบุ location_id'}, status=400)

    # ตรวจสอบว่า location_id เป็นตัวเลขหรือไม่
    try:
        location_id = int(location_id)
    except ValueError:
        return JsonResponse({'error': 'location_id ต้องเป็นตัวเลข'}, status=400)

    # ดึงข้อมูลจากฐานข้อมูล
    spots = ParkingSpot.objects.filter(location_id=location_id)
    if not spots.exists():  # กรณีไม่มีข้อมูลใน location_id นี้
        return JsonResponse({'error': 'ไม่มีข้อมูลช่องจอดสำหรับ location_id นี้'}, status=404)

    # สร้าง JSON response
    data = [
        {
            'spot_number': spot.spot_number,
            'is_available': spot.is_available,
        }
        for spot in spots
    ]

    return JsonResponse([
    {"id": spot.id, "is_available": spot.is_available} for spot in spots
], safe=False)




# easypark/views.py







from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ParkingLocation, ParkingSpot

def get_spot_details(request):
    location_id = request.GET.get('location_id')
    spot_id = request.GET.get('spot_id')

    # ตรวจสอบค่าที่ส่งเข้ามา
    if not location_id or not spot_id:
        return JsonResponse({'error': 'Missing location_id or spot_id'}, status=400)

    try:
        location = get_object_or_404(ParkingLocation, id=location_id)
        spot = get_object_or_404(ParkingSpot, id=spot_id, location=location)
    except:
        return JsonResponse({'error': 'Invalid location or spot ID'}, status=400)

    # ✅ เพิ่ม spot_number ลงไปใน response
    return JsonResponse({
        'spot_number': spot.spot_number,  # แก้จาก 'id': spot.id
        'is_available': spot.is_available,
        'reserved_by': spot.reserved_by.username if spot.reserved_by else None,
    })





    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_detail(request, spot_id):
    # ค้นหาข้อมูลที่จอดรถจาก ID ที่ส่งเข้ามา
    parking_spot = ParkingSpot.objects.get(id=spot_id)

    context = {
        'parking_spot': parking_spot,
    }
    return render(request, 'easypark/parking_details.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ParkingSpot
@login_required
def reserve_parking_spot(request, spot_id):
    spot = ParkingSpot.objects.get(id=spot_id)

    if spot.is_available:
        spot.is_available = False
        spot.reserved_by = request.user  # เก็บข้อมูลผู้ใช้งานที่ทำการจอง
        spot.save()

        return redirect('parking_detail')  # หลังจากจองเสร็จให้ไปยังหน้า parking_detail
    else:
        return render(request, 'error_page.html', {'message': 'ช่องจอดนี้ถูกจองแล้ว'})
    



from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import ParkingSpot
from django.contrib.auth.decorators import login_required

@login_required
def reserve_page(request, spot_number):
    location_id = request.GET.get('location_id')  # รับ location_id จาก URL
    print(f"Received spot_number: {spot_number}, location_id: {location_id}")

    try:
        # ดึงข้อมูลจากฐานข้อมูล
        if location_id:
            spot = ParkingSpot.objects.get(spot_number=spot_number, location_id=location_id)
        else:
            spot = ParkingSpot.objects.get(spot_number=spot_number)

        print(f"Spot found: {spot}")

        context = {
            'spot': spot,  # ส่งข้อมูล spot ไปที่ template
        }
        return render(request, 'easypark/reserve_page.html', context)
    except ParkingSpot.DoesNotExist:
        print("No spot found")
        return render(request, 'easypark/error.html', {'message': 'ไม่พบที่จอดรถที่คุณเลือก'})
    except ParkingSpot.MultipleObjectsReturned:
        print("Multiple spots found")
        return render(request, 'easypark/error.html', {'message': 'พบข้อมูลซ้ำในระบบ โปรดติดต่อผู้ดูแลระบบ'})






# ฟังก์ชันสำหรับยืนยันการจอง
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
@login_required
def confirm_reservation(request):
    if request.method == 'POST':
        print(request.POST)  # ตรวจสอบค่าที่ถูกส่งมาใน Terminal
        
        spot_number = request.POST.get('spot_number')
        location = request.POST.get('location')

        context = {
            'spot_number': spot_number,
            'location': location,
            'reservation_time': '08:00 - 08:15',
        }
        return render(request, 'easypark/reservation_confirmation.html', context)
    return redirect('homepage')




from django.shortcuts import redirect
def cancel_reservation(request):
    # Logic สำหรับการยกเลิกการจอง
    return redirect('homepage')






from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def sc_parking(request):
    context = {
        'spots': ParkingSpot.objects.filter(location__id = 1),
        'location': 'ตึกวิจัย',
        'locations': ParkingLocation.objects.all(),
    }
    if request.method == 'POST':
        location = request.POST.get('location')
        location = ParkingLocation.objects.get(pk=int(location))
        context['location'] = location
        context['spots'] = ParkingSpot.objects.filter(location = location)
    
    return render(request, 'easypark/sc_parking.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import ParkingSpot, ParkingLocation

@login_required
def add_parking_spot(request, location_id):
    location = get_object_or_404(ParkingLocation, id=location_id)

    # ตรวจสอบสิทธิ์ว่าเป็นเจ้าของสถานที่นี้
    if request.user != location.owner:
        return JsonResponse({"success": False, "error": "คุณไม่มีสิทธิ์เพิ่มช่องจอดที่นี่"}, status=403)

    if request.method == "POST":
        spot_number = request.POST.get("spot_number")

        # ตรวจสอบว่าช่องจอดนี้มีอยู่แล้วหรือไม่
        if ParkingSpot.objects.filter(location=location, spot_number=spot_number).exists():
            return JsonResponse({"success": False, "error": "❌ ช่องจอดนี้มีอยู่แล้ว"}, status=400)

        # บันทึกข้อมูลลงฐานข้อมูล
        new_spot = ParkingSpot.objects.create(
            location=location,
            spot_number=spot_number,
            is_available=True
        )

        return JsonResponse({
            "success": True,
            "message": "✅ เพิ่มช่องจอดเรียบร้อยแล้ว!",
            "spot_id": new_spot.id,
            "spot_number": new_spot.spot_number
        })

    return JsonResponse({"success": False, "error": "❌ วิธีการส่งข้อมูลไม่ถูกต้อง"}, status=400)








from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ParkingSpot

@csrf_exempt  # ✅ ปิด CSRF ตรวจสอบเฉพาะ POST
def delete_parking_spot(request, spot_id):
    if request.method == "POST":
        try:
            spot = ParkingSpot.objects.get(id=spot_id)
            spot.delete()
            return JsonResponse({"success": True, "message": "ช่องจอดถูกลบแล้ว!"})
        except ParkingSpot.DoesNotExist:
            return JsonResponse({"success": False, "error": "ไม่พบช่องจอดที่ต้องการลบ!"})
    return JsonResponse({"success": False, "error": "ไม่รองรับการร้องขอแบบนี้!"})

from django.shortcuts import render
from .models import CustomUser # ตรวจสอบให้แน่ใจว่าใช้ Model ที่ถูกต้อง

def user_management(request):
    user_roles = CustomUser.ROLE_CHOICES
    users = CustomUser.objects.all()
    return render(request, 'admin/user_management.html', {'users': users, 'user_roles': user_roles})


from django.shortcuts import render
from .models import ParkingLocation, CustomUser # ตรวจสอบให้แน่ใจว่าใช้ Model ที่ถูกต้อง

def locations_management(request):
    users = CustomUser.objects.all()
    locations = ParkingLocation.objects.all()
    return render(request, 'admin/locations_management.html', {'locations': locations, 'users': users})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import CustomUser  # ตรวจสอบให้แน่ใจว่าใช้ Model ที่ถูกต้อง

@csrf_exempt
def update_user(request, user_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = CustomUser.objects.get(id=user_id)
            user.username = data["username"]
            user.email = data["email"]
            user.role = data["role"]
            user.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser  # ใช้ Model ที่ถูกต้อง
import json

@csrf_exempt
def delete_user(request, user_id):
    if request.method == "DELETE":
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return JsonResponse({"success": True})
        except CustomUser.DoesNotExist:
            return JsonResponse({"success": False, "error": "ไม่พบผู้ใช้"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)


@csrf_exempt
def add_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_user = CustomUser.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=data["role"]
            )
            return JsonResponse({"success": True, "user_id": new_user.id})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "Method not allowed"}, status=405)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ParkingLocation
from django.contrib.auth import get_user_model
User = get_user_model()

@csrf_exempt
def edit_location(request, location_id):
    location = get_object_or_404(ParkingLocation, id=location_id)
    if request.method == "POST":
        print("📥 ข้อมูลที่รับมา:", request.POST)  # ✅ Debug
        print("📷 ไฟล์ที่แนบมา:", request.FILES)

        try:
            location.name = request.POST.get("name")
            location.description = request.POST.get("description")
            location.total_spots = request.POST.get("total_spots")
            location.available_spots = request.POST.get("available_spots")
            location.camera_url = request.POST.get("camera_url")

            owner_id = request.POST.get("owner")
            if owner_id:
                location.owner = get_object_or_404(User, id=owner_id)

            if "image" in request.FILES:
                location.image = request.FILES["image"]

            location.save()
            return JsonResponse({"success": True, "message": "สถานที่ถูกแก้ไขแล้ว"})
        except Exception as e:
            print("❌ Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})







@csrf_exempt
def delete_location(request, location_id):
    location = get_object_or_404(ParkingLocation, id=location_id)
    location.delete()
    return JsonResponse({"success": True, "message": "สถานที่ถูกลบแล้ว"})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ParkingLocation

@csrf_exempt
def get_location(request, location_id):
    location = get_object_or_404(ParkingLocation, id=location_id)
    
    data = {
        "id": location.id,
        "name": location.name,
        "description": location.description or "",
        "total_spots": location.total_spots,
        "available_spots": location.available_spots,
        "camera_url": location.camera_url or "",
        "owner": location.owner.id if location.owner else "",
        "image_url": location.image.url if location.image else None  # ✅ เช็คก่อนว่ามีภาพไหม
    }
    
    return JsonResponse({"success": True, "location": data})


from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ParkingLocation
from .forms import AdminLocationForm
from django.contrib import messages
from django.utils.text import slugify
@login_required
@csrf_exempt
def admin_add_location(request):
    """ให้ Admin เพิ่มสถานที่ โดยเลือกเจ้าของสถานที่เอง"""
    if request.method == "POST":
        try:
            print("📥 ข้อมูลที่รับมา:", request.POST)
            print("📷 ไฟล์ที่แนบมา:", request.FILES)

            name = request.POST.get("name")
            if not name:
                return JsonResponse({"success": False, "error": "Missing name"})

            description = request.POST.get("description", "")
            total_spots = request.POST.get("total_spots", "0")
            available_spots = request.POST.get("available_spots", "0")
            camera_url = request.POST.get("camera_url", "")
            owner_id = request.POST.get("owner")

            if not owner_id:
                return JsonResponse({"success": False, "error": "Missing owner ID"})

            owner = get_object_or_404(User, id=owner_id)
            image = request.FILES.get("image")

            # ✅ ป้องกันค่า slug ซ้ำ
            base_slug = slugify(name)
            unique_slug = base_slug
            counter = 1
            while ParkingLocation.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1

            # ✅ บันทึกข้อมูลใหม่
            location = ParkingLocation(
                name=name,
                slug=unique_slug,  # ✅ ใช้ slug ที่ไม่ซ้ำ
                description=description,
                total_spots=int(total_spots),
                available_spots=int(available_spots),
                camera_url=camera_url,
                owner=owner,
                image=image
            )
            location.save()

            # ✅ ส่งข้อมูลกลับไปให้ UI
            return JsonResponse({
                "success": True,
                "message": "สถานที่ถูกเพิ่มแล้ว",
                "location": {
                    "id": location.id,
                    "name": location.name
                }
            })
        except Exception as e:
            print("❌ Error:", str(e))
            return JsonResponse({"success": False, "error": str(e)})




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ParkingLocation
from .forms import AdminLocationForm

@login_required
@csrf_exempt
def admin_edit_location(request, location_id):
    """ให้ Admin แก้ไขสถานที่"""
    location = get_object_or_404(ParkingLocation, id=location_id)

    if request.method == "POST":
        print("📥 ข้อมูลที่รับมา:", request.POST)  # ✅ Debug ดูค่าที่ถูกส่ง
        print("📷 ไฟล์ที่แนบมา:", request.FILES)

        form = AdminLocationForm(request.POST, request.FILES, instance=location)
        if form.is_valid():
            form.save()
            print("✅ แก้ไขสำเร็จ:", form.cleaned_data)  # ✅ Debug ค่าหลังแก้ไข
            return JsonResponse(
                {"success": True, "message": "สถานที่ถูกแก้ไขแล้ว"},
                json_dumps_params={'ensure_ascii': False}
            )
        else:
            print("❌ ฟอร์มไม่ผ่าน:", form.errors)  # ✅ Debug ข้อผิดพลาด
            return JsonResponse(
                {"success": False, "error": form.errors},
                json_dumps_params={'ensure_ascii': False}
            )


    else:
        form = AdminLocationForm(instance=location)

    return render(request, 'admin_edit_location.html', {'form': form, 'location': location})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ParkingLocation

@csrf_exempt
def delete_location(request, location_id):
    """ฟังก์ชันลบสถานที่จอดรถ"""
    if request.method == "DELETE":
        try:
            location = get_object_or_404(ParkingLocation, id=location_id)
            location.delete()
            return JsonResponse({"success": True, "message": "สถานที่ถูกลบแล้ว"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})












