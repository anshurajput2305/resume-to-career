from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader
import os
import google.generativeai as genai
import traceback
import json
import re

app = FastAPI()

# === Configure Gemini API ===
genai.configure(api_key="AIzaSyCnS_QP3A-ACqbbtt1jn9N5AeQpLdwEfBA")

# === Skills List ===
skills = ["Python", "Java", "C++", "JavaScript", "React", "Django", "Flask"]

# === Paths ===
BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# === Serve static files ===
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# === Serve HTML at "/" ===
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = os.path.join(FRONTEND_DIR, "index.html")

    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# === Resume upload route ===
@app.post("/recommend_jobs")
async def recommend_jobs(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        text = ""
        reader = PdfReader(temp_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        os.remove(temp_path)

        if not text.strip():
            return {"error": "⚠️ No text found in PDF!"}

        print("✅ Extracted text:", text[:300])

        # Detect skills
        found_skills = [s for s in skills if s.lower() in text.lower()]
        print("✅ Found skills:", found_skills)

        # === Create prompt for Gemini ===
        prompt = f"""
You are a career recommendation assistant.

Analyze this resume text and the detected skills: {found_skills}.
Suggest 3-5 job roles that best match the candidate's background.
Provide the output in **JSON format only**, without markdown or backticks.
Resume text excerpt (max 500 chars): {text[:500]}
"""

        # === Call Gemini ===
        try:
            model = genai.GenerativeModel("models/gemini-2.5-flash")
            response = model.generate_content(prompt)
            model_output = response.text.strip()
            print("✅ Raw model output:", model_output[:500])

            # === Remove markdown backticks if present ===
            model_output = re.sub(r"^```json|```$", "", model_output, flags=re.IGNORECASE).strip()

            # === Parse JSON safely ===
            try:
                parsed_output = json.loads(model_output)
            except Exception:
                print("⚠️ JSON parse failed, returning raw output")
                parsed_output = {"raw_output": model_output}

        except Exception as e:
            print("❌ Gemini API error:")
            traceback.print_exc()
            return {"error": f"Gemini API failed: {str(e)}"}

        return {
            "extracted_skills": found_skills,
            "model_output": parsed_output
        }

    except Exception as e:
        print("❌ Unexpected error:")
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
