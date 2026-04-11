from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Diagnosis, Appointment, Prescription, PrescriptionRequest
from accounts.models import User
from .services.ai_diagnosis import analyze_symptoms

@login_required
def patient_dashboard(request):
    try:
        if request.user.role != 'patient':
            return redirect('doctor_dashboard')
        
        diagnoses = request.user.diagnoses.all().order_by('-created_at')
        appointments = request.user.patient_appointments.all().order_by('scheduled_time')
        prescription_requests = request.user.prescription_requests.all().order_by('-created_at')
        
        return render(request, 'telemedicine/patient_dashboard.html', {
            'diagnoses': diagnoses,
            'appointments': appointments,
            'prescription_requests': prescription_requests,
        })
    except Exception as e:
        return render(request, 'telemedicine/error_debug.html', {'error': str(e), 'view': 'Patient Dashboard'})

@login_required
def doctor_dashboard(request):
    try:
        if request.user.role != 'doctor':
            return redirect('patient_dashboard')
            
        appointments = request.user.doctor_appointments.all().order_by('scheduled_time')
        patients = User.objects.filter(role='patient')
        prescription_requests = PrescriptionRequest.objects.filter(status='pending').order_by('-created_at')
        return render(request, 'telemedicine/doctor_dashboard.html', {
            'appointments': appointments,
            'patients': patients,
            'prescription_requests': prescription_requests
        })
    except Exception as e:
        return render(request, 'telemedicine/error_debug.html', {'error': str(e), 'view': 'Doctor Dashboard'})

@login_required
def auto_diagnose(request):
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms')
        prescriptions = request.POST.get('prescriptions', '')
        
        result = analyze_symptoms(symptoms, prescriptions)
        
        Diagnosis.objects.create(
            patient=request.user,
            symptoms=symptoms,
            previous_prescriptions=prescriptions,
            malaria_risk=result['malaria_risk'],
            cholera_risk=result['cholera_risk'],
            suggested_steps=result['suggested_steps']
        )
        return redirect('patient_dashboard')
        
    return render(request, 'telemedicine/auto_diagnose.html')

@login_required
def request_prescription(request):
    if request.user.role != 'patient':
        return redirect('dashboard')
        
    if request.method == 'POST':
        notes = request.POST.get('patient_notes')
        PrescriptionRequest.objects.create(
            patient=request.user,
            patient_notes=notes
        )
        return redirect('patient_dashboard')
        
    return render(request, 'telemedicine/request_prescription.html')

@login_required
def review_prescription(request, request_id):
    if request.user.role != 'doctor':
        return redirect('dashboard')
        
    req = get_object_or_404(PrescriptionRequest, id=request_id)
    
    if request.method == 'POST':
        comments = request.POST.get('doctor_comments')
        req.doctor_comments = comments
        req.doctor = request.user
        req.status = 'reviewed'
        req.save()
        return redirect('doctor_dashboard')
        
    return render(request, 'telemedicine/review_prescription.html', {'req': req})

@login_required
def book_appointment(request):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
    
    doctors = User.objects.filter(role='doctor')
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        scheduled_time = request.POST.get('scheduled_time')
        notes = request.POST.get('notes')
        
        doctor = get_object_or_404(User, id=doctor_id, role='doctor')
        
        Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            scheduled_time=scheduled_time,
            notes=notes,
            status='pending'
        )
        return redirect('patient_dashboard')
        
    return render(request, 'telemedicine/book_appointment.html', {'doctors': doctors})

@login_required
@login_required
def confirm_appointment(request, appointment_id):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    appointment.status = 'confirmed'
    appointment.save()
    
    # Send Notification to Patient
    msg = f"Your appointment with Dr. {request.user.last_name} has been confirmed!"
    Notification.objects.create(recipient=appointment.patient, actor=request.user, message=msg, link="/dashboard/")
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notify_{appointment.patient.id}",
        {
            "type": "notify",
            "payload": {
                "message": msg,
                "link": "/dashboard/",
                "type": "appointment"
            }
        }
    )
    
    return redirect('doctor_dashboard')

@login_required
def patient_record_detail(request, patient_id):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
        
    patient = get_object_or_404(User, id=patient_id, role='patient')
    diagnoses = patient.diagnoses.all().order_by('-created_at')
    prescriptions = patient.prescriptions.all().order_by('-created_at')
    appointments = patient.patient_appointments.all().order_by('-scheduled_time')
    return render(request, 'telemedicine/patient_record.html', {
        'patient': patient,
        'diagnoses': diagnoses,
        'prescriptions': prescriptions,
        'appointments': appointments,
    })

@login_required
def complete_appointment(request, appointment_id):
    if request.user.role != 'doctor':
        return redirect('patient_dashboard')
        
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if request.method == 'POST':
        summary = request.POST.get('summary', '')
        appointment.notes = f"{appointment.notes}\n\n[Dr. Summary]: {summary}" if appointment.notes else f"[Dr. Summary]: {summary}"
        appointment.status = 'completed'
        appointment.save()
        
        # Trigger notification
        msg = f"Dr. {request.user.last_name} has completed your consultation."
        Notification.objects.create(recipient=appointment.patient, actor=request.user, message=msg, link="/dashboard/")
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notify_{appointment.patient.id}",
            {
                "type": "notify",
                "payload": {
                    "message": msg,
                    "link": "/dashboard/",
                    "type": "appointment"
                }
            }
        )
        
        return redirect('doctor_dashboard')
        
    return render(request, 'telemedicine/complete_appointment.html', {'appointment': appointment})

    return render(request, 'telemedicine/complete_appointment.html', {'appointment': appointment})
