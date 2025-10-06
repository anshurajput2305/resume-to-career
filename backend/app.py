from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import requests
import os

app = FastAPI()

# === HuggingFace API Config ===
HUGGINGFACE_API_TOKEN = "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"
HF_MODEL_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

# === Skills & Job Mappings ===
skills_list = [
    "python", "java", "c++", "javascript", "react", "node", "sql",
    "ml", "ai", "data", "html", "css", "django", "flask", "mongodb",
    "aws", "devops", "linux", "typescript", "angular", "nlp",
    "cloud", "docker", "kubernetes", "excel", "communication",
]

job_map = {
    "python": ["Python Developer", "Data Scientist", "Automation Engineer"],
    "java": ["Java Developer", "Backend Engineer"],
    "ml": ["Machine Learning Engineer", "AI Researcher"],
    "react": ["Frontend Developer", "Full Stack Engineer"],
    "sql": ["Database Engineer", "Data Analyst"],
    "aws": ["Cloud Engineer", "DevOps Engineer"],
    "excel": ["Business Analyst", "Project Manager"],
}

# === Templates & Static Files ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(BASE_DIR, "../frontend")

templates = Jinja2Templates(directory=frontend_dir)

# Serve entire frontend folder without making static/
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# === Helpers ===
def extract_text_from_file(file: UploadFile):
    text = ""
    if file.filename.endswith(".pdf"):
        with fitz.open(stream=file.file.read(), filetype="pdf") as pdf:
            for page in pdf:
                text += page.get_text("text")
    elif file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        image = Image.open(io.BytesIO(file.file.read()))
        text = pytesseract.image_to_string(image)
    else:
        text = file.file.read().decode("utf-8", errors="ignore")
    return text


def extract_skills(text):
    text_lower = text.lower()
    return [skill for skill in skills_list if skill in text_lower]


def get_job_recommendations(skills):
    all_jobs = []
    for skill in skills:
        all_jobs.extend(job_map.get(skill, []))
    return list(set(all_jobs))


def score_jobs_with_huggingface(text, jobs):
    payload = {"inputs": text, "parameters": {"candidate_labels": jobs}}
    response = requests.post(HF_MODEL_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return list(zip(result["labels"], result["scores"]))
    return []


# === Routes ===
@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    text = extract_text_from_file(file)
    extracted_skills = extract_skills(text)
    recommended_jobs = get_job_recommendations(extracted_skills)
    hf_results = score_jobs_with_huggingface(text, recommended_jobs)

    return {
        "extracted_skills": extracted_skills,
        "recommended_jobs": [
            {"title": job, "score": round(score * 100, 2)}
            for job, score in hf_results
        ] if hf_results else [{"title": j, "score": None} for j in recommended_jobs],
    }
