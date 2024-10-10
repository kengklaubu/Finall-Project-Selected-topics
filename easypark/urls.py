from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('redirect-parking/', views.redirect_parking, name='redirect_parking'),
    path('hospital-parking/<str:date>/', views.hospital_parking, name='hospital_parking'),
    path('sc-parking/<str:date>/', views.sc_parking, name='sc_parking'),
    path('parking-c/<str:date>/', views.parking_c, name='parking_c'),
    path('parking-d/<str:date>/', views.parking_d, name='parking_d'),
    path('parking-e/<str:date>/', views.parking_e, name='parking_e'),
    path('parking-f/<str:date>/', views.parking_f, name='parking_f'),
    path('parking-g/<str:date>/', views.parking_g, name='parking_g'),
    path('parking-h/<str:date>/', views.parking_h, name='parking_h'),
    path('parking-i/<str:date>/', views.parking_i, name='parking_i'),
    path('parking-j/<str:date>/', views.parking_j, name='parking_j'),
    path('get-parking-status/', views.get_parking_status, name='get_parking_status'),  # สำหรับ AJAX ที่ดึงสถานะที่จอด
    path('get-spot-details/', views.get_spot_details, name='get_spot_details'),  # สำหรับ AJAX ที่ดึงรายละเอียดที่จอดรถ
    path('reserve_page/<int:spot_number>/', views.reserve_page, name='reserve_page'),  # ส่งค่า spot_number ไปหน้า reserve_page
    path('confirm_reservation/', views.confirm_reservation, name='confirm_reservation'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('parking-location/<str:location>/<str:date>/', views.parking_location, name='parking_location'),
]
