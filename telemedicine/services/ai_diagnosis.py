def analyze_symptoms(symptoms_text, prescriptions_text=""):
    """
    Rule-based engine for evaluating malaria and cholera risk.
    Returns:
    {
        'malaria_risk': 'Low' | 'Medium' | 'High',
        'cholera_risk': 'Low' | 'Medium' | 'High',
        'suggested_steps': str
    }
    """
    symptoms = symptoms_text.lower()
    
    # Malaria Keywords
    malaria_high = ['fever', 'chills', 'sweat', 'shivering', 'bitter taste']
    malaria_med = ['headache', 'fatigue', 'nausea', 'muscle ache', 'vomiting']
    
    # Cholera Keywords
    cholera_high = ['watery diarrhea', 'severe diarrhea', 'dehydration', 'sunken eyes']
    cholera_med = ['vomiting', 'leg cramps', 'thirst', 'restlessness']
    
    malaria_score = sum([1 for word in malaria_high if word in symptoms]) * 2 + \
                    sum([1 for word in malaria_med if word in symptoms])
                    
    cholera_score = sum([1 for word in cholera_high if word in symptoms]) * 2 + \
                    sum([1 for word in cholera_med if word in symptoms])
                    
    malaria_risk = 'Low'
    if malaria_score >= 4:
        malaria_risk = 'High'
    elif malaria_score >= 2:
        malaria_risk = 'Medium'
        
    cholera_risk = 'Low'
    if cholera_score >= 4:
        cholera_risk = 'High'
    elif cholera_score >= 2:
        cholera_risk = 'Medium'
        
    steps = []
    if malaria_risk == 'High' or cholera_risk == 'High':
        steps.append("URGENT: Please book an appointment with a doctor immediately. High risk detected.")
    elif malaria_risk == 'Medium' or cholera_risk == 'Medium':
        steps.append("Please monitor your symptoms closely and schedule a consultation with a doctor if they persist.")
    else:
        steps.append("Your symptoms indicate a low risk for Malaria and Cholera. Rest and maintain good hygiene.")
        
    return {
        'malaria_risk': malaria_risk,
        'cholera_risk': cholera_risk,
        'suggested_steps': " ".join(steps)
    }

def generate_consultation_summary(patient_name, symptoms, malaria_risk, cholera_risk):
    """
    Generates a professional clinical summary for the doctor.
    """
    summary = f"MEDICAL CONSULTATION SUMMARY\n"
    summary += f"Patient: {patient_name}\n"
    summary += f"Condition: Assessment for Malaria/Cholera\n\n"
    
    summary += f"CLINICAL PRESENTATION:\n"
    summary += f"The patient presents with the following reported symptoms: {symptoms}.\n\n"
    
    summary += f"AI DIAGNOSTIC ASSESSMENT:\n"
    summary += f"- Malaria Risk: {malaria_risk}\n"
    summary += f"- Cholera Risk: {cholera_risk}\n\n"
    
    summary += f"RECOMMENDATION:\n"
    if malaria_risk == 'High' or cholera_risk == 'High':
        summary += "Immediate clinical intervention and lab confirmation required. Patient is in a high-risk category. Monitor vital signs closely."
    else:
        summary += "Baseline observation. If symptoms persist or worsen within 48 hours, escalate to full diagnostic panel."
        
    return summary
