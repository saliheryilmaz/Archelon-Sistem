from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('yeni/', views.create_appointment, name='create'),
    path('<int:pk>/iptal/', views.cancel_appointment, name='cancel'),
    path('<int:pk>/onayla/', views.confirm_appointment, name='confirm'),
    path('egitmenler/', views.instructor_list, name='instructor_list'),
    path('egitmenler/yeni/', views.instructor_create, name='instructor_create'),
    path('egitmenler/<int:pk>/duzenle/', views.instructor_edit, name='instructor_edit'),
    path('egitmenler/<int:pk>/sil/', views.instructor_delete, name='instructor_delete'),
    path('yoklama/', views.attendance_sheet, name='attendance_sheet'),
    path('yoklama/kaydet/', views.save_attendance, name='save_attendance'),
    path('uye-paketleri/', views.member_packages_json, name='member_packages_json'),
    path('egitmen-raporu/', views.instructor_report, name='instructor_report'),
]
