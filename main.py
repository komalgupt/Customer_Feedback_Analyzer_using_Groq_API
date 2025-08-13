from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from groq_agent import analyze_feedback
import os
import uuid
import re
from utils import extract_feedbacks_from_file, save_results_to_excel

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_post(
    request: Request,
    feedback: str = Form(""),
    file: UploadFile = File(None)
):
    results = []
    feedbacks = []

    # File upload case
    if file:
        feedbacks = extract_feedbacks_from_file(file)

    # Manual typing case
    if feedback.strip():
        raw_inputs = re.split(r'\n|;|\|\|', feedback)
        feedbacks.extend([line.strip() for line in raw_inputs if line.strip()])

    # Remove duplicates & clean
    feedbacks = list(dict.fromkeys(feedbacks))

    for fb in feedbacks:
        result = analyze_feedback(fb)
        # Force consistent JSON structure for HTML template
        results.append({
            "input": fb,
            "themes": result.get("themes", ""),
            "sentiment": result.get("sentiment", ""),
            "highlights": result.get("highlights", "")
        })

    # Save results to Excel if available
    download_link = None
    if results:
        filename = f"feedback_results_{uuid.uuid4().hex[:8]}.xlsx"
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        save_results_to_excel(results, filepath)
        download_link = f"/download/{filename}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "feedback": feedback if not file else "",  # clear manual text if file uploaded
        "result": results,
        "download_link": download_link
    })

@app.get("/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(DOWNLOAD_DIR, filename)
    return FileResponse(path=filepath, filename=filename, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.post("/api/analyze", response_class=JSONResponse)
async def analyze_api(feedback: dict):
    text = feedback.get("text", "")
    result = analyze_feedback(text)
    return result
