import requests
import csv
from django.shortcuts import render
import csv
import os
from django.conf import settings

def get_sheet_data():
    # ระบุพาธของไฟล์ CSV ในโปรเจค
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

from django.shortcuts import render

def login_page(request):
    return render(request, 'easypark/login.html')  # ชี้ไปยังไฟล์ login.html


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm

def register_page(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created successfully!")
            return redirect('login_page')  # Redirect ไปหน้า Login หลังสมัครเสร็จ
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    
    return render(request, 'easypark/register.html', {'form': form})



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_page(request):
    return render(request, 'easypark/profile.html', {'user': request.user})




import os
import csv
from django.conf import settings
from django.shortcuts import render

def homepage(request):
    # เส้นทางไฟล์ CSV ในโฟลเดอร์ static
    file_path = os.path.join(settings.BASE_DIR, 'static/data/data_10.csv')
    
    locations = []
    if os.path.exists(file_path):  # ตรวจสอบว่าไฟล์มีอยู่
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # ข้าม header
            for row in reader:
                locations.append(row[0])
    else:
        print("ไฟล์ CSV ไม่พบในโปรเจค")

    context = {
        'locations': locations,
    }
    return render(request, 'easypark/home.html', context)



from django.shortcuts import render
from .models import ParkingSpot
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_location(request, location, date):
    # ตรวจสอบว่า location และ date ถูกต้อง
    if not location or not date:
        return render(request, 'easypark/error.html', {'message': 'ข้อมูลที่คุณส่งมาไม่ถูกต้อง'})

    # ค้นหาที่จอดรถจากฐานข้อมูลตาม location และ date
    parking_spots = ParkingSpot.objects.filter(location=location, date=date)
    
    # ถ้าไม่พบที่จอดรถ
    if not parking_spots.exists():
        return render(request, 'easypark/error.html', {'message': 'ไม่พบที่จอดรถที่ตรงกับข้อมูลที่ค้นหา'})
    
    context = {
        'parking_spots': parking_spots,
        'location': location,
        'date': date,
    }
    
    return render(request, 'easypark/parking_location.html', context)



from django.http import JsonResponse
from .models import ParkingSpot

def get_parking_status(request):
    spots = ParkingSpot.objects.all()
    data = [{'spot_number': spot.spot_number, 'is_available': spot.is_available} for spot in spots]
    return JsonResponse(data, safe=False)




from django.http import JsonResponse
from .models import ParkingSpot

def get_spot_details(request):
    spot_number = request.GET.get('spot')
    try:
        spot = ParkingSpot.objects.select_related('reserved_by').get(spot_number=spot_number)
        response_data = {
            'spot_number': spot.spot_number,
            'reserved_by': spot.reserved_by.username if spot.reserved_by else 'ว่าง',
            'license_plate': spot.license_plate if spot.license_plate else 'ไม่มีข้อมูล',
        }
        return JsonResponse(response_data)
    except ParkingSpot.DoesNotExist:
        return JsonResponse({'error': 'ไม่พบข้อมูลช่องจอดนี้'}, status=404)
    
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
# ฟังก์ชันแสดงหน้า reserve_page พร้อมแสดงข้อมูลที่จอง
@login_required
def reserve_page(request, spot_number):
    # ดึงข้อมูลรายละเอียดของที่จอดรถจาก spot_number
    try:
        spot = ParkingSpot.objects.get(spot_number=spot_number)
        context = {
            'spot_number': spot.spot_number,
            'location': spot.location,
            'date': spot.date,  # ต้องมีข้อมูล date
        }
        return render(request, 'easypark/reserve_page.html', context)
    except ParkingSpot.DoesNotExist:
        return render(request, 'error.html', {'message': 'ไม่พบที่จอดรถที่คุณเลือก'})



# ฟังก์ชันสำหรับยืนยันการจอง
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
@login_required
def confirm_reservation(request):
    if request.method == 'POST':
        # ดึงรายละเอียดการจองจาก POST request
        spot_number = request.POST.get('spot_number')
        location = request.POST.get('location')

        context = {
            'spot_number': spot_number,
            'location': location,
            'reservation_time': '08:00 - 08:15',  # เวลาจอดรถ (สามารถเปลี่ยนตามเงื่อนไขได้)
        }
        return render(request, 'easypark/reservation_confirmation.html', context)
    return redirect('homepage')


from django.shortcuts import redirect
def cancel_reservation(request):
    # Logic สำหรับการยกเลิกการจอง
    return redirect('homepage')

from django.shortcuts import redirect
@login_required
def redirect_parking(request):
    # รับค่า location และ date จาก request
    location = request.GET.get('location')
    date = request.GET.get('date')

    # ตรวจสอบว่ามี location และ date หรือไม่
    if not location or not date:
        # หากไม่มี location หรือ date ให้ส่งกลับไปหน้า error หรือแจ้งเตือน
        return render(request, 'easypark/error.html', {'message': 'กรุณาเลือกสถานที่จอดรถและวันที่เข้าจอด'})

    # ตรวจสอบ location และเปลี่ยนเส้นทางไปยัง view ที่เหมาะสม
    if location == 'โรงพยาบาล':
        return redirect('hospital_parking', date=date)
    elif location == 'ตึกวิจัย':
        return redirect('sc_parking', date=date)
    elif location == 'ลานจอด C':
        return redirect('parking_c', date=date)
    elif location == 'ลานจอด D':
        return redirect('parking_d', date=date)
    elif location == 'ลานจอด E':
        return redirect('parking_e', date=date)
    elif location == 'ลานจอด F':
        return redirect('parking_f', date=date)
    elif location == 'ลานจอด G':
        return redirect('parking_g', date=date)
    elif location == 'ลานจอด H':
        return redirect('parking_h', date=date)
    elif location == 'ลานจอด I':
        return redirect('parking_i', date=date)
    elif location == 'ลานจอด J':
        return redirect('parking_j', date=date)
    else:
        return redirect('homepage')

    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def hospital_parking(request, date):
    # นำข้อมูลที่จอดรถสำหรับโรงพยาบาลมาแสดง
    context = {
        'date': date,
        'location': 'โรงพยาบาล',
    }
    return render(request, 'easypark/hospital_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def sc_parking(request, date):
    context = {
        'date': date,
        'location': 'ตึกวิจัย',
    }
    return render(request, 'easypark/sc_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_c(request, date):
    # นำข้อมูลที่จอดรถสำหรับลานจอด C มาแสดง
    context = {
        'date': date,
        'location': 'ลานจอด C',
    }
    return render(request, 'easypark/ABC_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_d(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด D',
    }
    return render(request, 'easypark/ABC_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_e(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด E',
    }
    return render(request, 'easypark/ABC_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_f(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด F',
    }
    return render(request, 'easypark/ABC_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_g(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด G',
    }
    return render(request, 'easypark/ABC_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_h(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด H',
    }
    return render(request, 'easypark/ABC_parking.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_i(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด I',
    }
    return render(request, 'easypark/ABC_parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def parking_j(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด J',
    }
    return render(request, 'easypark/ABC_parking.html', context)






















