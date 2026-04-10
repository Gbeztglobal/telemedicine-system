from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Diagnosis, Appointment, Prescription, PrescriptionRequest
from accounts.models import User
from .services.ai_diagnosis import analyze_symptoms

@login_required
def patient_dashboard(request):
    if request.user.role != 'patient':
        return redirect('doctor_dashboard')
    
    diagnoses = request.user.diagnoses.all().order_by('-created_at')
    appointments = request.user.patient_appointments.all().order_by('scheduled_time')
    prescription_requests = request.user.prescription_requests.all().order_by('-created_at')
    return render(request, 'telemedicine/patient_dashboard.html', {
        'diagnoses': diagnoses,
        'appointments': appointments,
        'prescription_requests': prescription_requests
    })

@login_required
def doctor_dashboard(request):
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
