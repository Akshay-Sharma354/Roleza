from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.browser import router as browser_router


app = FastAPI(title="Roleza API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(browser_router)


@app.get("/")
def home():
    return {"message": "Welcome to Roleza 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/jobs")
def get_jobs():
    return {
        "jobs": [
            {
                "id": 1,
                "title": "Junior AI Engineer",
                "company": "Nova Intelligence",
                "source": "Company career page",
                "posted": "Posted today",
                "location": "India",
                "work_mode": "Remote",
                "experience": "Entry level",
                "description": (
                    "Build AI-powered workflows, work with language models, "
                    "and support production automation systems."
                ),
                "resume": "AI Resume",
                "status": "Ready to apply",
                "requires_human_review": False,
            },
            {
                "id": 2,
                "title": "AI Automation Associate",
                "company": "FlowForge Labs",
                "source": "Startup job board",
                "posted": "Posted 3 hours ago",
                "location": "Worldwide",
                "work_mode": "Remote",
                "experience": "Fresher friendly",
                "description": (
                    "Help create internal AI agents, test prompts, document "
                    "workflows, and improve automation quality."
                ),
                "resume": "AI Resume",
                "status": "Human review needed",
                "requires_human_review": True,
            },
        ]
    }