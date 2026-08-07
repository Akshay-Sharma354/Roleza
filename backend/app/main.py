from datetime import datetime
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

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


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "roleza.db"
RESUME_DIR = BASE_DIR / "resumes"


RESUME_FILES = {
    "AI": RESUME_DIR / "Akshay-Sharma_AI.pdf",
    "US IT Recruiter": RESUME_DIR / "Akshay-Sharma_BDM.docx",
}


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
        "job_url": "https://example.com/jobs/roleza-ai-1",
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
        "job_url": "https://example.com/jobs/roleza-ai-2",
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
        "resume": "BDM Resume",
        "status": "Ready to apply",
        "requires_human_review": False,
        "job_url": "https://example.com/jobs/roleza-bdm-1",
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
        "resume": "BDM Resume",
        "status": "Ready to apply",
        "requires_human_review": False,
        "job_url": "https://example.com/jobs/blocked-company",
    },
]


class ApplicationCreate(BaseModel):
    job_id: int
    title: str
    company: str
    role_type: str
    location: str
    work_mode: str
    source: str
    resume: str
    status: str
    requires_human_review: bool = False
    job_url: str = ""


class ApplicationUpdate(BaseModel):
    status: str


def get_database_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_database_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL UNIQUE,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                role_type TEXT NOT NULL,
                location TEXT NOT NULL,
                work_mode TEXT NOT NULL,
                source TEXT NOT NULL,
                resume TEXT NOT NULL,
                status TEXT NOT NULL,
                requires_human_review INTEGER NOT NULL DEFAULT 0,
                applied_at TEXT NOT NULL,
                job_url TEXT NOT NULL DEFAULT ''
            )
            """
        )

        columns = connection.execute(
            """
            PRAGMA table_info(applications)
            """
        ).fetchall()

        column_names = [
            column["name"]
            for column in columns
        ]

        if "job_url" not in column_names:
            connection.execute(
                """
                ALTER TABLE applications
                ADD COLUMN job_url TEXT NOT NULL DEFAULT ''
                """
            )

        connection.commit()


def application_row_to_dict(row):
    return {
        "id": row["id"],
        "job_id": row["job_id"],
        "title": row["title"],
        "company": row["company"],
        "role_type": row["role_type"],
        "location": row["location"],
        "work_mode": row["work_mode"],
        "source": row["source"],
        "resume": row["resume"],
        "status": row["status"],
        "requires_human_review": bool(
            row["requires_human_review"]
        ),
        "applied_at": row["applied_at"],
        "job_url": row["job_url"],
    }


def is_blocked_company(company_name: str) -> bool:
    normalized_name = company_name.strip().lower()

    return any(
        blocked_company in normalized_name
        for blocked_company in BLOCKED_COMPANIES
    )


def get_resume_for_role(role_type: str):
    resume_path = RESUME_FILES.get(role_type)

    if resume_path is None:
        return None

    return {
        "role_type": role_type,
        "filename": resume_path.name,
        "path": str(resume_path),
        "exists": resume_path.exists(),
    }


initialize_database()


@app.get("/")
def home():
    return {
        "message": "Welcome to Roleza 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


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

        if (
            role_type != "Both"
            and job["role_type"] != role_type
        ):
            continue

        if (
            remote_only
            and job["work_mode"].lower() != "remote"
        ):
            continue

        if location not in [
            "Remote worldwide",
            "Worldwide",
        ]:
            job_location = job["location"].lower()
            requested_location = location.lower()

            if (
                requested_location not in job_location
                and job_location != "worldwide"
            ):
                continue

        job_copy = dict(job)

        resume_info = get_resume_for_role(
            job_copy["role_type"]
        )

        if resume_info:
            job_copy["resume_filename"] = (
                resume_info["filename"]
            )

            job_copy["resume_exists"] = (
                resume_info["exists"]
            )

        filtered_jobs.append(job_copy)

    return {
        "jobs": filtered_jobs,
        "blocked_companies": BLOCKED_COMPANIES,
    }


@app.get("/resumes")
def get_resumes():
    return {
        "resumes": [
            {
                "role_type": "AI",
                "display_name": "AI Resume",
                "filename": RESUME_FILES["AI"].name,
                "exists": RESUME_FILES["AI"].exists(),
            },
            {
                "role_type": "US IT Recruiter",
                "display_name": "BDM Resume",
                "filename": RESUME_FILES[
                    "US IT Recruiter"
                ].name,
                "exists": RESUME_FILES[
                    "US IT Recruiter"
                ].exists(),
            },
        ]
    }


@app.get("/resumes/{role_type}")
def download_resume(role_type: str):
    if role_type not in RESUME_FILES:
        raise HTTPException(
            status_code=404,
            detail="Resume type not found.",
        )

    resume_path = RESUME_FILES[role_type]

    if not resume_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Resume file is missing.",
        )

    return FileResponse(
        path=resume_path,
        filename=resume_path.name,
        media_type="application/octet-stream",
    )


@app.get("/applications")
def get_applications():
    with get_database_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM applications
            ORDER BY id DESC
            """
        ).fetchall()

    return {
        "applications": [
            application_row_to_dict(row)
            for row in rows
        ]
    }


@app.post(
    "/applications",
    status_code=201,
)
def create_application(
    application: ApplicationCreate,
):
    if is_blocked_company(application.company):
        raise HTTPException(
            status_code=403,
            detail=(
                "Applications to this company "
                "are blocked."
            ),
        )

    resume_path = RESUME_FILES.get(
        application.role_type
    )

    if resume_path is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No resume is configured for "
                "this role type."
            ),
        )

    if not resume_path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "The selected resume file is missing."
            ),
        )

    applied_at = datetime.now().isoformat(
        timespec="seconds"
    )

    try:
        with get_database_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO applications (
                    job_id,
                    title,
                    company,
                    role_type,
                    location,
                    work_mode,
                    source,
                    resume,
                    status,
                    requires_human_review,
                    applied_at,
                    job_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application.job_id,
                    application.title,
                    application.company,
                    application.role_type,
                    application.location,
                    application.work_mode,
                    application.source,
                    resume_path.name,
                    application.status,
                    int(
                        application.requires_human_review
                    ),
                    applied_at,
                    application.job_url,
                ),
            )

            connection.commit()

            application_id = cursor.lastrowid

    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail=(
                "This job is already in your "
                "application tracker."
            ),
        ) from error

    return {
        "application": {
            "id": application_id,
            "job_id": application.job_id,
            "title": application.title,
            "company": application.company,
            "role_type": application.role_type,
            "location": application.location,
            "work_mode": application.work_mode,
            "source": application.source,
            "resume": resume_path.name,
            "status": application.status,
            "requires_human_review": (
                application.requires_human_review
            ),
            "applied_at": applied_at,
            "job_url": application.job_url,
        }
    }


@app.patch("/applications/{application_id}")
def update_application(
    application_id: int,
    update: ApplicationUpdate,
):
    with get_database_connection() as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM applications
            WHERE id = ?
            """,
            (application_id,),
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=404,
                detail="Application not found.",
            )

        connection.execute(
            """
            UPDATE applications
            SET status = ?
            WHERE id = ?
            """,
            (
                update.status,
                application_id,
            ),
        )

        connection.commit()

        updated_row = connection.execute(
            """
            SELECT *
            FROM applications
            WHERE id = ?
            """,
            (application_id,),
        ).fetchone()

    return {
        "application": application_row_to_dict(
            updated_row
        )
    }


@app.delete("/applications/{application_id}")
def delete_application(
    application_id: int,
):
    with get_database_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM applications
            WHERE id = ?
            """,
            (application_id,),
        )

        connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Application not found.",
        )

    return {
        "message": (
            "Application removed successfully."
        )
    }