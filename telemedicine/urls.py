from django.urls import path
from . import views

urlpatterns = [
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('auto-diagnose/', views.auto_diagnose, name='auto_diagnose'),
    path('prescription/request/', views.request_prescription, name='request_prescription'),
    path('prescription/review/<int:request_id>/', views.review_prescription, name='review_prescription'),
    path('appointment/book/', views.book_appointment, name='book_appointment'),
    path('appointment/confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('appointment/complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('patient-record/<int:patient_id>/', views.patient_record_detail, name='patient_record_detail'),
]
