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
@login_required
@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    return render(request, 'easypark/admin_dashboard.html')

# หน้าแดชบอร์ดของผู้จัดการ (Manager)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from easypark.models import Reservation, ParkingSpot, CustomUser

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ParkingLocation, Reservation

@login_required
def manager_dashboard(request):
    # ตรวจสอบว่าเป็น Manager
    if request.user.role != 'manager':
        return redirect('homepage')  # ถ้าไม่ใช่ Manager ให้กลับไปหน้า Homepage

    # ดึงข้อมูลสถานที่ทั้งหมด
    locations = ParkingLocation.objects.all()
    
    # ดึงข้อมูลการจองทั้งหมด โดยใช้ select_related เพื่อดึงข้อมูลที่เชื่อมโยงไปยัง CustomUser
    reservations = Reservation.objects.select_related('parking_spot', 'user', 'parking_spot__location', 'parking_spot__reserved_by')

    context = {
        'locations': locations,
        'reservations': reservations,
    }
    return render(request, 'easypark/manager_dashboard.html', context)




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



from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_page(request):
    return render(request, 'easypark/profile.html', {'user': request.user})

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
    # เส้นทางไฟล์ CSV ในโฟลเดอร์ static
    file_path = os.path.join(settings.BASE_DIR, 'static/data/data_10.csv')
   
    locations = []
    if os.path.exists(file_path): 
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  
            for row in reader:
                locations.append(row[0])
    else:
        print("ไฟล์ CSV ไม่พบในโปรเจค")

    # ถ้า user ยังไม่ได้ล็อกอิน ก็แสดงหน้า homepage แบบปกติ
    if request.user.is_authenticated:
        # ตรวจสอบ role ของผู้ใช้ที่ล็อกอิน
        if request.user.role == 'admin':
            return redirect('admin_dashboard')  # เปลี่ยนไปหน้าแดชบอร์ดของแอดมิน
        elif request.user.role == 'manager':
            return redirect('manager_dashboard')  # เปลี่ยนไปหน้าแดชบอร์ดของผู้จัดการ
        else:
            return render(request, 'easypark/home.html', {'locations': locations})  # สำหรับผู้ใช้ทั่วไป
    else:
        # ถ้าผู้ใช้ไม่ได้ล็อกอิน ก็ให้แสดงหน้า homepage
        return render(request, 'easypark/home.html', {'locations': locations})


    








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
    return JsonResponse(data, safe=False)








from django.http import JsonResponse
from .models import ParkingSpot

def get_spot_details(request):
    location_id = request.GET.get('location_id')
    spot_number = request.GET.get('spot')

    # ตรวจสอบว่า location_id และ spot_number ถูกส่งมาหรือไม่
    if not location_id or not spot_number:
        return JsonResponse({'error': 'กรุณาระบุ location_id และ spot_number'}, status=400)
    
    try:
        spot = ParkingSpot.objects.get(location_id=location_id, spot_number=spot_number)
        response_data = {
            'spot_number': spot.spot_number,
            'is_available': spot.is_available,
            'reserved_by': spot.reserved_by.username if spot.reserved_by else 'ว่าง',
            'license_plate': spot.license_plate if spot.license_plate else None,
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
    elif location == 'อาคารเรียนรวม 4':
        return redirect('CLB_4', date=date)
    elif location == 'อาคารเรียนรวม 5':
        return redirect('CLB_5', date=date)
    elif location == 'อาคารศิลปะศาสตร์':
        return redirect('LA_Parking', date=date)
    elif location == 'ตึกบริหาร':
        return redirect('Bus_Parking', date=date)
    elif location == 'อาคาร Co-work':
        return redirect('Cowork_Parking', date=date)
    elif location == 'ตึกเคมี':
        return redirect('CHLAB_Parking', date=date)
    elif location == 'ตึกพยาบาล':
        return redirect('NU_Parking', date=date)
    elif location == 'ตึกเภสัช':
        return redirect('PH_Parking', date=date)
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
def CLB_4(request, date):
    # นำข้อมูลที่จอดรถสำหรับลานจอด C มาแสดง
    context = {
        'date': date,
        'location': 'อาคารเรียนรวม 4',
    }
    return render(request, 'easypark/CLB_4.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def CLB_5(request, date):
    context = {
        'date': date,
        'location': 'อาคารเรียนรวม 5',
    }
    return render(request, 'easypark/CLB_5.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def LA_Parking(request, date):
    context = {
        'date': date,
        'location': 'อาคารศิลปะศาสตร์',
    }
    return render(request, 'easypark/LA_Parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def Bus_Parking(request, date):
    context = {
        'date': date,
        'location': 'ตึกบริหาร',
    }
    return render(request, 'easypark/Bus_Parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def Cowork_Parking(request, date):
    context = {
        'date': date,
        'location': 'อาคาร Co-work',
    }
    return render(request, 'easypark/Cowork_Parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def CHLAB_Parking(request, date):
    context = {
        'date': date,
        'location': 'ตึกเคมี',
    }
    return render(request, 'easypark/CHLAB_Parking.html', context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def NU_Parking(request, date):
    context = {
        'date': date,
        'location': 'ตึกพยาบาล',
    }
    return render(request, 'easypark/NU_Parking.html', context)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required
def PH_Parking(request, date):
    context = {
        'date': date,
        'location': 'ตึกเภสัช',
    }
    return render(request, 'easypark/PH_Parking.html', context)






















