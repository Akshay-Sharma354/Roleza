from fastapi import FastAPI, Query
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


BLOCKED_COMPANIES = [
    "akkodis",
    "modis",
    "klaxontech",
    "adecco",
]


JOBS = [
    {
        "id": 1,
        "role_type": "AI",
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
        "role_type": "AI",
        "title": "AI Automation Associate",
        "company": "FlowForge Labs",
        "source": "Startup job board",
        "posted": "Posted 3 hours ago",
        "location": "Worldwide",
        "work_mode": "Remote",
        "experience": "Fresher friendly",
        "description": (
            "Help create internal AI agents, test prompts, document workflows, "
            "and improve automation quality."
        ),
        "resume": "AI Resume",
        "status": "Human review needed",
        "requires_human_review": True,
    },
    {
        "id": 3,
        "role_type": "US IT Recruiter",
        "title": "US IT Recruiter",
        "company": "TalentBridge Solutions",
        "source": "Company career page",
        "posted": "Posted today",
        "location": "India",
        "work_mode": "Remote",
        "experience": "3+ years",
        "description": (
            "Manage full-cycle US IT hiring, source technical candidates, "
            "and coordinate interviews with US-based clients."
        ),
        "resume": "US IT Resume",
        "status": "Ready to apply",
        "requires_human_review": False,
    },
    {
        "id": 4,
        "role_type": "US IT Recruiter",
        "title": "Senior Technical Recruiter",
        "company": "Akkodis India",
        "source": "Company career page",
        "posted": "Posted 2 hours ago",
        "location": "India",
        "work_mode": "Remote",
        "experience": "4+ years",
        "description": (
            "Recruit technical professionals for enterprise clients "
            "across the United States."
        ),
        "resume": "US IT Resume",
        "status": "Ready to apply",
        "requires_human_review": False,
    },
]


def is_blocked_company(company_name: str) -> bool:
    normalized_name = company_name.strip().lower()

    return any(
        blocked_company in normalized_name
        for blocked_company in BLOCKED_COMPANIES
    )


@app.get("/")
def home():
    return {"message": "Welcome to Roleza 🚀"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/jobs")
def get_jobs(
    role_type: str = Query(default="Both"),
    location: str = Query(default="India"),
    remote_only: bool = Query(default=True),
):
    filtered_jobs = []

    for job in JOBS:
        if is_blocked_company(job["company"]):
            continue

        if role_type != "Both" and job["role_type"] != role_type:
            continue

        if remote_only and job["work_mode"].lower() != "remote":
            continue

        if location not in ["Remote worldwide", "Worldwide"]:
            job_location = job["location"].lower()
            requested_location = location.lower()

            if (
                requested_location not in job_location
                and job_location != "worldwide"
            ):
                continue

        filtered_jobs.append(job)

    return {
        "jobs": filtered_jobs,
        "blocked_companies": BLOCKED_COMPANIES,
    }