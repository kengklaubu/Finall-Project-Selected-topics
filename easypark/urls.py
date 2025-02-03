from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('redirect-parking/', login_required(views.redirect_parking), name='redirect_parking'),
    path('hospital-parking/<str:date>/', login_required(views.hospital_parking), name='hospital_parking'),
    path('sc-parking/', login_required(views.sc_parking), name='sc_parking'),
    path('CHLAB-Parking/<str:date>/', login_required(views.CHLAB_Parking), name='CHLAB_Parking'),
    path('CLB_4/<str:date>/', login_required(views.CLB_4), name='CLB_4'),
    path('CLB_5/<str:date>/', login_required(views.CLB_5), name='CLB_5'),
    path('LA_Parking/<str:date>/', login_required(views.LA_Parking), name='LA_Parking'),
    path('Bus_Parking/<str:date>/', login_required(views.Bus_Parking), name='Bus_Parking'),
    path('Cowork_Parking/<str:date>/', login_required(views.Cowork_Parking), name='Cowork_Parking'),
    path('NU_Parking/<str:date>/', login_required(views.NU_Parking), name='NU_Parking'),
    path('PH_Parking/<str:date>/', login_required(views.PH_Parking), name='PH_Parking'),
    path('api/get_parking_status', views.get_parking_status, name='get_parking_status'),
    path('api/get_spot_details', views.get_spot_details, name='get_spot_details'),
    path('reserve_page/<int:spot_number>/', login_required(views.reserve_page), name='reserve_page'),
    path('confirm_reservation/', login_required(views.confirm_reservation), name='confirm_reservation'),
    path('cancel_reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('login/',(views.login_page), name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('profile/', login_required(views.profile_page), name='profile'),
    path('accounts/login/', LoginView.as_view(template_name='easypark/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', views.password_reset, name='password_reset1221'),
    #path('locations/', views.locations_page, name='locations'),
    path('locations/<slug:location_slug>/', views.parking_location, name='parking-location'),
    path('reservation_history/', views.reservation_history, name='reservation_history'),
    path('login/', views.login_page, name='login_page'),  
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  
    path('manager_dashboard/<int:location_id>/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/reservation/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    #path('manager/parking/suspend/<int:spot_id>/', views.suspend_parking_spot, name='suspend_parking_spot'),
    path('get_parking_spots/<int:location_id>/', views.get_parking_spots, name='get_parking_spots'),
    path('suspend_parking_spot/<int:spot_id>/', views.suspend_parking_spot, name='suspend_parking_spot'),
    path('start-detection/', views.start_detection, name='start_detection'),
    path('live/<int:location_id>/',views.stream_video, name='live_video'),
    path('stream/<int:location_id>/',views.video_feed, name='video_feed'),
    
    


    

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    
]
