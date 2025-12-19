from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import numpy as np
from skfuzzy import control as ctrl
import os

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# --- CORS SETTINGS (Critical for Frontend to talk to Backend) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow your Vite app to access this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Build the full path to the .pkl file
model_path = os.path.join(BASE_DIR, "NeuroSymbolic_System_v1.pkl")

# --- LOAD THE BRAIN ---
# We load this once when the server starts to save time
try:
    system_data = joblib.load(model_path)
    neural_models = system_data['neural_models']
    fuzzy_brain_system = system_data['fuzzy_brain'] # This is the ControlSystem
    model_features = system_data['features']
    print("✅ Neuro-Symbolic System Loaded Successfully")
    
    # Reconstruct the Simulation (Simulations cannot be pickled easily, so we rebuild it)
    fuzzy_sim = ctrl.ControlSystemSimulation(fuzzy_brain_system)
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    system_data = None

# --- INPUT DATA MODEL (Validation) ---
class StudentProfile(BaseModel):
    Name: str
    ANXMAT: float    # 1.0 to 4.0
    BELONG: float    # -2.0 to 2.0 (approx)
    ESCS: float      # -2.0 to 2.0
    TEACHSUP: float  # -2.0 to 2.0
    BULLIED: float   # -2.0 to 2.0
    ICTRES: float    # -2.0 to 2.0
    Gender: str      # "Male" or "Female"

# MOUNT THE FRONTEND
# 1. Mount the "assets" folder (CSS/JS)
app.mount("/assets", StaticFiles(directory="/app/frontend/dist/assets"), name="assets")

# 2. Serve index.html at the root
@app.get("/")
async def read_index():
    return FileResponse("/app/frontend/dist/index.html")

# --- THE LOGIC ENDPOINT ---
@app.post("/analyze")
async def analyze_student(student: StudentProfile):
    if not system_data:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # 1. PREPARE DATA
        gender_num = 1 if student.Gender.lower() == 'female' else 2
        
        input_data = {
            'ANXMAT': student.ANXMAT,
            'BELONG': student.BELONG,
            'ESCS': student.ESCS,
            'TEACHSUP': student.TEACHSUP,
            'BULLIED': student.BULLIED,
            'ICTRES': student.ICTRES,
            'Gender_Num': gender_num
        }
        
        input_df = pd.DataFrame([input_data])
        input_df = input_df[model_features]

        # 2. NEURAL PREDICTIONS (XGBoost)
        risks = {}
        for subject, model in neural_models.items():
            probs = model.predict_proba(input_df)[0]
            fail_prob = (probs[0] + probs[1]) * 100 
            
            # --- FIX 1: Convert numpy.float to python float ---
            risks[subject] = float(round(fail_prob, 2)) 

        weakest_subject = max(risks, key=risks.get)
        max_risk = risks[weakest_subject]

        # 3. SYMBOLIC MODEL (Fuzzy)
        f_anxiety = min(10, max(0, (student.ANXMAT - 1) * 3.3))
        f_support = min(10, max(0, (student.TEACHSUP + 2) * 2.5))

        fuzzy_sim.input['anxiety'] = f_anxiety
        fuzzy_sim.input['support'] = f_support
        fuzzy_sim.compute()
        
        # --- FIX 2: Convert numpy.float to python float ---
        symbolic_risk = float(fuzzy_sim.output['risk_factor'])

        # 4. DIAGNOSIS
        advisory = {
            "status": "Stable",
            "message": "Student is generally stable.",
            "color": "green",
            "flags": []
        }

        # Logic Checks (Using the standard python floats now)
        if symbolic_risk > 60:
            advisory["status"] = "Critical"
            advisory["message"] = "Psychosocial Alert: Severe Anxiety detected without support."
            advisory["color"] = "red"
            advisory["flags"].append("Counseling Required")
        
        elif f_anxiety > 7 and f_support > 7:
            advisory["status"] = "Monitor"
            advisory["message"] = "Buffer Activated: High Anxiety mitigated by Teacher Support."
            advisory["color"] = "blue"
            advisory["flags"].append("Reinforce Confidence")

        elif max_risk > 70:
            advisory["status"] = "At-Risk"
            advisory["message"] = f"High probability of failure in {weakest_subject[3:]}."
            advisory["color"] = "orange"
            
            if student.ICTRES < -1:
                advisory["flags"].append("Digital Poverty (Low ICT)")
            if student.BULLIED > 0:
                advisory["flags"].append("Social Exclusion/Bullying")
            if student.Gender.lower() == 'male' and weakest_subject == 'PV1READ':
                advisory["flags"].append("Gender Gap (Reading)")

        # Return JSON
        return {
            "name": student.Name,
            "neural_risks": risks,
            "fuzzy_score": float(round(symbolic_risk, 2)), # --- FIX 3: Explicit cast here too ---
            "advisory": advisory
        }

    except Exception as e:
        print(f"Error: {e}") # Print error to terminal for debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Neuro-Symbolic Advisor API is Running"}