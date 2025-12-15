import os
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
from typing import List
import tempfile
from dotenv import load_dotenv

load_dotenv()

# Set up Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

# Enable CORS for localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"]
)

@app.post("/generate-schedule")
async def generate_schedule(
    students: UploadFile = File(...),
    teachers: UploadFile = File(...),
    slots: UploadFile = File(...),
    busy: UploadFile = File(...)
):
    # Read CSVs into DataFrames
    df_students = pd.read_csv(students.file)
    df_teachers = pd.read_csv(teachers.file)
    df_slots = pd.read_csv(slots.file)
    df_busy = pd.read_csv(busy.file)

    # Filter students needing remedial
    df_students = df_students[df_students['Score'] < 40]

    # Prepare prompt for Gemini
    prompt = f"""
You are a scheduling assistant. Given the following data, generate a remedial class schedule as a JSON array. Each entry must have: Student Name, Subject, Teacher Name, Slot_ID. STRICTLY obey these rules:
- A student can only be scheduled in a slot if their Section is NOT busy in that slot (see busy.csv).
- A teacher can only be assigned if they are free in that slot (see teachers.csv Slot_IDs).
- Each student must be scheduled for their failing subject with a teacher who teaches that subject.
- Do NOT assign a student to more than one slot per subject.
- Output ONLY valid assignments. If a student cannot be scheduled, omit them from the output.

---
Failing Students (students.csv):
{df_students.to_json(orient='records')}

Teachers (teachers.csv):
{df_teachers.to_json(orient='records')}

Slots (slots.csv):
{df_slots.to_json(orient='records')}

Section Busy Slots (busy.csv):
{df_busy.to_json(orient='records')}

Output JSON array ONLY. Example:
[
  {{"Student Name": "...", "Subject": "...", "Teacher Name": "...", "Slot_ID": "..."}}
]
"""

    # Call Gemini
    # Call Gemini
    # Switching to gemini-flash-latest (last resort)
    model = genai.GenerativeModel("gemini-flash-latest")
    generation_config = genai.GenerationConfig(temperature=0.0)
    
    try:
        response = model.generate_content(prompt, generation_config=generation_config, request_options={"timeout": 600})
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
    # Extract JSON from response
    import json
    import re
    match = re.search(r'\[.*\]', response.text, re.DOTALL)
    if match:
        schedule = json.loads(match.group(0))
    else:
        return JSONResponse(status_code=500, content={"error": "No valid schedule returned by Gemini."})

    return schedule
