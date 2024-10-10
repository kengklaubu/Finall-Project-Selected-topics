import requests
import csv
from django.shortcuts import render


def get_sheet_data():
    # URL ที่ได้จากการ Publish Google Sheets เป็น CSV
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRUdSdqMza7Rt2BYlbrwkSI6ccSk5DEBd7EWfKpg0tIHKYJdZ7d7FKfiJcvt9eR9ZSIadOhEvMdOgGb/pub?output=csv'
    response = requests.get(url)
    decoded_content = response.content.decode('utf-8')
    reader = csv.reader(decoded_content.splitlines(), delimiter=',')
    data = list(reader)

    return data

def homepage(request):
    # ดึงข้อมูลจาก Google Sheets
    sheet_data = get_sheet_data()

    context = {
        'sheet_data': sheet_data,  # ส่งข้อมูลไปยัง template
    }
    return render(request, 'easypark/home.html', context)


from django.shortcuts import render
from .models import ParkingSpot

def parking_location(request, location, date):
    # ค้นหาที่จอดรถจากฐานข้อมูลตาม location และ date
    parking_spots = ParkingSpot.objects.filter(location=location, date=date)
    
    context = {
        'parking_spots': parking_spots,
        'location': location,
        'date': date,
    }
    
    return render(request, 'easypark/parking_detail.html', context)









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
            'reservation_time': spot.date,  # ตัวอย่างการใช้ข้อมูลการจอง
        }
        return render(request, 'easypark/reserve_page.html', context)
    except ParkingSpot.DoesNotExist:
        return render(request, 'error.html', {'message': 'ไม่พบที่จอดรถที่คุณเลือก'})


# ฟังก์ชันสำหรับยืนยันการจอง
from django.shortcuts import render, redirect

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

def cancel_reservation(request):
    # Logic สำหรับการยกเลิกการจอง
    return redirect('homepage')


from django.shortcuts import redirect
from .models import ParkingSpot

def redirect_parking(request):
    location = request.GET.get('location')
    date = request.GET.get('date')

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
        return redirect('homepage')  # กลับไปหน้าหลักหากไม่มีที่จอดตรงกับ location
    
from django.shortcuts import render


def hospital_parking(request, date):
    # นำข้อมูลที่จอดรถสำหรับโรงพยาบาลมาแสดง
    context = {
        'date': date,
        'location': 'โรงพยาบาล',
    }
    return render(request, 'easypark/hospital_parking.html', context)

def sc_parking(request, date):
    context = {
        'date': date,
        'location': 'ตึกวิจัย',
    }
    return render(request, 'easypark/sc_parking.html', context)

from django.shortcuts import render

def parking_c(request, date):
    # นำข้อมูลที่จอดรถสำหรับลานจอด C มาแสดง
    context = {
        'date': date,
        'location': 'ลานจอด C',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_d(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด D',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_e(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด E',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_f(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด F',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_g(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด G',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_h(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด H',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_i(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด I',
    }
    return render(request, 'easypark/ABC_parking.html', context)

def parking_j(request, date):
    context = {
        'date': date,
        'location': 'ลานจอด J',
    }
    return render(request, 'easypark/ABC_parking.html', context)






















