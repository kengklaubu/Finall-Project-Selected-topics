from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('redirect-parking/', login_required(views.redirect_parking), name='redirect_parking'),
    path('hospital-parking/<str:date>/', login_required(views.hospital_parking), name='hospital_parking'),
    path('sc-parking/<str:date>/', login_required(views.sc_parking), name='sc_parking'),
    path('parking-c/<str:date>/', login_required(views.parking_c), name='parking_c'),
    path('parking-d/<str:date>/', login_required(views.parking_d), name='parking_d'),
    path('parking-e/<str:date>/', login_required(views.parking_e), name='parking_e'),
    path('parking-f/<str:date>/', login_required(views.parking_f), name='parking_f'),
    path('parking-g/<str:date>/', login_required(views.parking_g), name='parking_g'),
    path('parking-h/<str:date>/', login_required(views.parking_h), name='parking_h'),
    path('parking-i/<str:date>/', login_required(views.parking_i), name='parking_i'),
    path('parking-j/<str:date>/', login_required(views.parking_j), name='parking_j'),
    path('get-parking-status/', views.get_parking_status, name='get_parking_status'),  # สำหรับ AJAX ที่ดึงสถานะที่จอด
    path('get-spot-details/', views.get_spot_details, name='get_spot_details'),  # สำหรับ AJAX ที่ดึงรายละเอียดที่จอดรถ
    path('reserve_page/<int:spot_number>/', login_required(views.reserve_page), name='reserve_page'),  # ส่งค่า spot_number ไปหน้า reserve_page
    path('confirm_reservation/', login_required(views.confirm_reservation), name='confirm_reservation'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('parking-location/<str:location>/<str:date>/', views.parking_location, name='parking_location'),
    path('login/',(views.login_page), name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('profile/', login_required(views.profile_page), name='profile'),
    path('accounts/login/', LoginView.as_view(template_name='easypark/login.html'), name='login'),
    
]
