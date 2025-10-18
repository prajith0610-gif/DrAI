from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from geopy.distance import geodesic
import json
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Doctor database
doctors = [
    {"name": "Dr. Ravi", "specialty": "General", "lat": 12.9716, "lon": 77.5946, "language": "English"},
    {"name": "Dr. Priya", "specialty": "Pediatrics", "lat": 12.9352, "lon": 77.6245, "language": "Tamil"},
    {"name": "Dr. Suresh", "specialty": "Cardiology", "lat": 12.9719, "lon": 77.6412, "language": "Hindi"}
]

# Ambulance database (simulated)
ambulances = [
    {"id": "AMB001", "lat": 12.9720, "lon": 77.6200},
    {"id": "AMB002", "lat": 12.9800, "lon": 77.6100}
]

# Symptom-disease mapping
symptom_disease_map = {
    frozenset(["fever", "cough"]): ["Common Cold 🤧", "Flu 🦠", "COVID-19 😷"],
    frozenset(["headache"]): ["Migraine 💥", "Tension Headache 😖"],
    frozenset(["stomach pain", "vomiting"]): ["Gastritis 🤢", "Food Poisoning 🍔"],
    frozenset(["chest pain"]): ["Heart-related issue ❤️", "Muscle Strain 💪"],
    frozenset(["rash", "itching"]): ["Allergy 🤧", "Chickenpox 🐣"],
    frozenset(["fatigue", "weight loss", "fever"]): ["Tuberculosis 🫁", "Anemia 🩸"],
    frozenset(["sore throat", "runny nose"]): ["Cold 🤧", "Sinus Infection 🤒"],
    frozenset(["joint pain", "swelling"]): ["Arthritis 🦴", "Gout 💥"],
    frozenset(["blurred vision", "headache"]): ["Migraine 💥", "Glaucoma 👁️"],
    frozenset(["diarrhea", "dehydration"]): ["Food Poisoning 🍔", "Cholera 💦"],
    frozenset(["shortness of breath", "cough"]): ["Asthma 🌬️", "Pneumonia 🫁"],
    frozenset(["nosebleed", "fatigue"]): ["Anemia 🩸", "Hypertension 🩺"],
    frozenset(["abdominal pain", "constipation"]): ["IBS 🥴", "Gastritis 🤢"],
    frozenset(["dizziness", "nausea"]): ["Low BP 🩺", "Vertigo 🤢"],
    frozenset(["swelling", "pain", "redness"]): ["Infection 🦠", "Cellulitis 🩹"],
    frozenset(["thirst", "frequent urination"]): ["Diabetes 🩸", "Dehydration 💧"]
}

UNKNOWN_FILE = "unknown_symptoms.json"

def save_unknown_symptoms(symptoms_list, suggested_disease=None):
    data = {"entries": []}
    if os.path.exists(UNKNOWN_FILE):
        with open(UNKNOWN_FILE, "r") as f:
            data = json.load(f)
    data["entries"].append({
        "symptoms": symptoms_list,
        "suggested_disease": suggested_disease
    })
    with open(UNKNOWN_FILE, "w") as f:
        json.dump(data, f, indent=4)

def diagnose_symptoms(user_symptoms):
    user_set = set(user_symptoms)
    matched_diseases = set()

    # Known mapping
    for symptoms_set, diseases in symptom_disease_map.items():
        if symptoms_set <= user_set or len(user_set & symptoms_set) > 0:
            matched_diseases.update(diseases)

    # Check unknown learned symptoms
    if os.path.exists(UNKNOWN_FILE):
        with open(UNKNOWN_FILE, "r") as f:
            unknown_data = json.load(f)
        for entry in unknown_data["entries"]:
            if set(entry["symptoms"]) <= user_set and entry["suggested_disease"]:
                matched_diseases.add(entry["suggested_disease"])

    # If no match, learn
    if not matched_diseases:
        save_unknown_symptoms(user_symptoms)
        return ["No match found. Dr.AI has learned these symptoms and will improve next time. 🇮🇳🤖"]

    return list(matched_diseases)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None, "doctors": None, "ambulances": ambulances})

@app.post("/", response_class=HTMLResponse)
def diagnose(request: Request, symptoms: str = Form(...), lat: float = Form(...), lon: float = Form(...), language: str = Form(...)):
    user_symptoms = [s.strip().lower() for s in symptoms.split(",")]

    diseases = diagnose_symptoms(user_symptoms)

    # Nearby doctors
    nearby_doctors = []
    user_location = (lat, lon)
    for doc in doctors:
        doc_location = (doc["lat"], doc["lon"])
        distance = geodesic(user_location, doc_location).km
        if distance <= 15 and doc["language"].lower() == language.lower():
            nearby_doctors.append(doc)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": diseases,
        "symptoms": symptoms,
        "doctors": nearby_doctors,
        "ambulances": ambulances,
        "user_lat": lat,
        "user_lon": lon
    })
