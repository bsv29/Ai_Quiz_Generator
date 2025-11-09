import json
import os
import traceback
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from .database import SessionLocal, init_db, Quiz
from .scraper import scrape_wikipedia
from .llm_quiz_generator import LLMQuizGenerator

import os

# Initialize DB if needed
init_db()

app = FastAPI(title="AI Wiki Quiz Generator")

# Allow all origins for development. Change in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve a minimal static frontend so the app can be tested without running npm/Vite
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(BASE_DIR, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def root():
    idx = os.path.join(static_dir, "index.html")
    if os.path.exists(idx):
        return FileResponse(idx)
    return {"status": "ok", "message": "AI Wiki Quiz Generator backend is running"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class GenerateRequest(BaseModel):
    url: str


@app.post("/generate_quiz")
def generate_quiz(req: GenerateRequest, db: Session = Depends(get_db)):
    url = req.url.strip()
    
    # Basic URL validation
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(
            status_code=400, 
            detail="Invalid URL format. Please include http:// or https://"
        )
    
    try:
        title, clean_text = scrape_wikipedia(url)
    except ValueError as e:
        # User-friendly validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        # Connection errors
        raise HTTPException(
            status_code=503, 
            detail=f"Unable to connect to Wikipedia. Please check your internet connection and try again. Error: {str(e)}"
        )
    except Exception as e:
        # Log full traceback to a file for debugging
        tb = traceback.format_exc()
        log_path = os.path.join(os.path.dirname(__file__), 'error.log')
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"--- SCRAPE ERROR for URL: {url} ---\n")
            f.write(tb + "\n")
        error_msg = f"An unexpected error occurred while processing the URL: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

    generator = LLMQuizGenerator()
    quiz = generator.generate_quiz(title, clean_text, num_questions=6)
    quiz["source_url"] = url

    # persist
    quiz_record = Quiz(
        url=url,
        title=title,
        scraped_content=clean_text,
        full_quiz_data=json.dumps(quiz, ensure_ascii=False),
    )
    db.add(quiz_record)
    db.commit()
    db.refresh(quiz_record)

    # attach id
    quiz["id"] = quiz_record.id

    return quiz


@app.get("/history")
def history(db: Session = Depends(get_db)) -> List[dict]:
    rows = db.query(Quiz).order_by(Quiz.date_generated.desc()).all()
    return [
        {
            "id": r.id,
            "url": r.url,
            "title": r.title,
            "date_generated": r.date_generated.isoformat(),
        }
        for r in rows
    ]


@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    r = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    payload = json.loads(r.full_quiz_data)
    payload["id"] = r.id
    payload["url"] = r.url
    return payload


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=True)
