from datetime import datetime
from hashlib import sha256
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.routes.browser import router as browser_router
from app.services.job_sources import fetch_all_live_jobs
from app.services.job_scoring import score_job


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


MAX_TOTAL_JOBS = 80
MAX_SEARCH_CARDS_TOTAL = 45
MAX_REAL_JOBS_TOTAL = 35
MAX_SEARCH_CARDS_PER_SOURCE_ROLE = 6
MAX_REAL_JOBS_PER_SOURCE = 15


PRIORITY_SOURCE_ORDER = {
    "Indeed India": 100,
    "Naukri": 95,
    "LinkedIn": 90,
    "Cutshort": 80,
    "Wellfound": 75,
    "Greenhouse": 65,
    "Company Watchlist": 60,
    "Arbeitnow Backup": 20,
    "Remote OK Backup": 15,
}


TARGET_NCR_TERMS = [
    "india",
    "remote india",
    "noida",
    "gurgaon",
    "gurugram",
    "delhi",
    "delhi ncr",
    "ncr",
]


BLOCKED_LOCATION_TERMS = [
    "usa",
    "united states",
    "remote us",
    "remote usa",
    "us remote",
    "san francisco",
    "new york",
    "washington, dc",
    "washington d.c",
    "london",
    "united kingdom",
    " uk",
    "uk ",
    "berlin",
    "germany",
    "remote europe",
    "remote - europe",
    "europe only",
    "latin america",
    "colombia",
    "brazil",
    "argentina",
    "chile",
    "mexico",
    "türkiye",
    "turkey",
    "emea",
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
    remote_eligibility: str = "Unknown"


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
                job_url TEXT NOT NULL DEFAULT '',
                remote_eligibility TEXT NOT NULL DEFAULT 'Unknown'
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

        if "remote_eligibility" not in column_names:
            connection.execute(
                """
                ALTER TABLE applications
                ADD COLUMN remote_eligibility
                TEXT NOT NULL DEFAULT 'Unknown'
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
        "remote_eligibility": row["remote_eligibility"],
    }


def is_blocked_company(
    company_name: str,
) -> bool:
    normalized_name = (
        company_name
        or ""
    ).strip().lower()

    return any(
        blocked_company in normalized_name
        for blocked_company in BLOCKED_COMPANIES
    )


def get_resume_for_role(
    role_type: str,
):
    resume_path = RESUME_FILES.get(
        role_type
    )

    if resume_path is None:
        return None

    return {
        "role_type": role_type,
        "filename": resume_path.name,
        "path": str(resume_path),
        "exists": resume_path.exists(),
    }


def create_stable_job_id(
    external_id: str,
) -> int:
    digest = sha256(
        external_id.encode("utf-8")
    ).digest()

    return int.from_bytes(
        digest[:8],
        byteorder="big",
    ) & 0x7FFFFFFFFFFFFFFF


def normalize_text(value: str) -> str:
    return (
        value
        or ""
    ).strip().lower()


def location_has_blocked_region_for_india(
    job_location: str,
) -> bool:
    location = normalize_text(
        job_location
    )

    return any(
        phrase in location
        for phrase in BLOCKED_LOCATION_TERMS
    )


def location_has_target_india_region(
    job_location: str,
) -> bool:
    location = normalize_text(
        job_location
    )

    return any(
        phrase in location
        for phrase in TARGET_NCR_TERMS
    )


def location_matches(
    job_location: str,
    requested_location: str,
    remote_eligibility: str,
) -> bool:
    job_location_lower = normalize_text(
        job_location
    )

    requested_lower = normalize_text(
        requested_location
    )

    eligibility = (
        remote_eligibility
        or "Unknown"
    )

    eligibility_lower = normalize_text(
        eligibility
    )

    if requested_location in [
        "Remote worldwide",
        "Worldwide",
    ]:
        return eligibility_lower in [
            "worldwide",
            "india",
            "unknown",
        ]

    if requested_location == "India":
        if eligibility in [
            "Worldwide",
            "India",
        ]:
            return True

        if location_has_target_india_region(
            job_location
        ):
            return True

        if (
            eligibility == "Unknown"
            and "remote" in job_location_lower
            and not location_has_blocked_region_for_india(
                job_location
            )
        ):
            return True

        return False

    if requested_location in [
        "Noida",
        "Gurgaon",
        "Gurugram",
        "Delhi",
        "Delhi NCR",
    ]:
        if requested_lower in job_location_lower:
            return True

        if (
            requested_location == "Delhi NCR"
            and any(
                term in job_location_lower
                for term in [
                    "noida",
                    "gurgaon",
                    "gurugram",
                    "delhi",
                    "ncr",
                ]
            )
        ):
            return True

        if eligibility in [
            "Worldwide",
            "India",
        ]:
            return True

        return False

    if requested_location == "Singapore":
        return (
            "singapore" in job_location_lower
            or eligibility == "Worldwide"
        )

    if requested_location == "Dubai":
        return (
            "dubai" in job_location_lower
            or "uae" in job_location_lower
            or "united arab emirates" in job_location_lower
            or eligibility == "Worldwide"
        )

    if requested_location == "Thailand":
        return (
            "thailand" in job_location_lower
            or eligibility == "Worldwide"
        )

    if requested_lower in job_location_lower:
        return True

    return eligibility == "Worldwide"


def source_rank(
    source: str,
) -> int:
    return PRIORITY_SOURCE_ORDER.get(
        source,
        0,
    )


def is_search_card(
    job,
) -> bool:
    return bool(
        job.get("is_search_card")
    )


def decorate_job(
    job,
):
    external_id = job.get(
        "external_id",
        job.get(
            "job_url",
            "",
        ),
    )

    if not external_id:
        return None

    job_copy = dict(job)

    job_copy["id"] = create_stable_job_id(
        external_id
    )

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

        job_copy["resume"] = (
            "BDM Resume"
            if job_copy["role_type"]
            == "US IT Recruiter"
            else "AI Resume"
        )

    if (
        job_copy.get(
            "remote_eligibility"
        )
        == "Unknown"
    ):
        job_copy[
            "requires_human_review"
        ] = True

    job_copy["status"] = (
        "Needs human review"
        if job_copy.get(
            "requires_human_review",
            False,
        )
        else "Ready to apply"
    )

    job_copy = score_job(
        job_copy
    )

    return job_copy


def should_keep_job(
    job,
    role_type,
    location,
    remote_only,
):
    company = job.get(
        "company",
        "",
    )

    if is_blocked_company(
        company
    ):
        return False

    if (
        role_type != "Both"
        and job.get("role_type") != role_type
    ):
        return False

    if (
        remote_only
        and not job.get(
            "remote",
            False,
        )
    ):
        return False

    if not location_matches(
        job_location=job.get(
            "location",
            "",
        ),
        requested_location=location,
        remote_eligibility=job.get(
            "remote_eligibility",
            "Unknown",
        ),
    ):
        return False

    return True


def limit_search_cards(
    jobs,
):
    selected = []
    counts = {}

    search_cards = [
        job
        for job in jobs
        if is_search_card(job)
    ]

    search_cards.sort(
        key=lambda item: (
            source_rank(
                item.get(
                    "source",
                    "",
                )
            ),
            item.get(
                "fit_score",
                0,
            ),
            item.get(
                "created_at",
                0,
            ),
        ),
        reverse=True,
    )

    for job in search_cards:
        if len(selected) >= MAX_SEARCH_CARDS_TOTAL:
            break

        key = (
            job.get("source"),
            job.get("role_type"),
        )

        current_count = counts.get(
            key,
            0,
        )

        if (
            current_count
            >= MAX_SEARCH_CARDS_PER_SOURCE_ROLE
        ):
            continue

        counts[key] = current_count + 1

        selected.append(
            job
        )

    return selected


def limit_real_jobs(
    jobs,
):
    selected = []
    counts = {}

    real_jobs = [
        job
        for job in jobs
        if not is_search_card(job)
    ]

    real_jobs.sort(
        key=lambda item: (
            item.get(
                "fit_score",
                0,
            ),
            source_rank(
                item.get(
                    "source",
                    "",
                )
            ),
            item.get(
                "created_at",
                0,
            ),
        ),
        reverse=True,
    )

    for job in real_jobs:
        if len(selected) >= MAX_REAL_JOBS_TOTAL:
            break

        source = job.get(
            "source",
            "Unknown",
        )

        current_count = counts.get(
            source,
            0,
        )

        if current_count >= MAX_REAL_JOBS_PER_SOURCE:
            continue

        counts[source] = current_count + 1

        selected.append(
            job
        )

    return selected


def build_focused_job_list(
    jobs,
):
    search_cards = limit_search_cards(
        jobs
    )

    real_jobs = limit_real_jobs(
        jobs
    )

    focused_jobs = (
        search_cards
        + real_jobs
    )

    focused_jobs.sort(
        key=lambda item: (
            item.get(
                "fit_score",
                0,
            ),
            source_rank(
                item.get(
                    "source",
                    "",
                )
            ),
            item.get(
                "created_at",
                0,
            ),
        ),
        reverse=True,
    )

    return focused_jobs[:MAX_TOTAL_JOBS]


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
    role_type: str = Query(
        default="Both"
    ),
    location: str = Query(
        default="India"
    ),
    remote_only: bool = Query(
        default=True
    ),
):
    try:
        live_result = fetch_all_live_jobs()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Roleza encountered an error "
                "while loading live jobs."
            ),
        ) from error

    live_jobs = live_result.get(
        "jobs",
        [],
    )

    source_errors = live_result.get(
        "source_errors",
        [],
    )

    sources = live_result.get(
        "sources",
        [],
    )

    all_filtered_jobs = []

    for job in live_jobs:
        if not should_keep_job(
            job=job,
            role_type=role_type,
            location=location,
            remote_only=remote_only,
        ):
            continue

        job_copy = decorate_job(
            job
        )

        if job_copy is None:
            continue

        age_days = job_copy.get(
            "age_days"
        )

        if age_days is None:
            continue

        if age_days > 30:
            continue

        all_filtered_jobs.append(
            job_copy
        )

    focused_jobs = build_focused_job_list(
        all_filtered_jobs
    )

    high_priority_count = sum(
        1
        for job in focused_jobs
        if job.get(
            "priority"
        ) == "High"
    )

    medium_priority_count = sum(
        1
        for job in focused_jobs
        if job.get(
            "priority"
        ) == "Medium"
    )

    search_card_count = sum(
        1
        for job in focused_jobs
        if is_search_card(job)
    )

    real_job_count = (
        len(focused_jobs)
        - search_card_count
    )

    return {
        "jobs": focused_jobs,

        "total": len(
            focused_jobs
        ),

        "total_before_focus_limit": len(
            all_filtered_jobs
        ),

        "high_priority": (
            high_priority_count
        ),

        "medium_priority": (
            medium_priority_count
        ),

        "search_cards": (
            search_card_count
        ),

        "real_jobs": (
            real_job_count
        ),

        "sources": sources,

        "live": True,

        "source_errors": source_errors,

        "blocked_companies": (
            BLOCKED_COMPANIES
        ),

        "focus_note": (
            "Roleza is showing the best limited set of jobs/search cards "
            "instead of flooding the dashboard."
        ),
    }


@app.get("/resumes")
def get_resumes():
    return {
        "resumes": [
            {
                "role_type": "AI",
                "display_name": "AI Resume",
                "filename": (
                    RESUME_FILES["AI"].name
                ),
                "exists": (
                    RESUME_FILES["AI"].exists()
                ),
            },
            {
                "role_type": "US IT Recruiter",
                "display_name": "BDM Resume",
                "filename": (
                    RESUME_FILES[
                        "US IT Recruiter"
                    ].name
                ),
                "exists": (
                    RESUME_FILES[
                        "US IT Recruiter"
                    ].exists()
                ),
            },
        ]
    }


@app.get(
    "/resumes/{role_type}"
)
def download_resume(
    role_type: str,
):
    if role_type not in RESUME_FILES:
        raise HTTPException(
            status_code=404,
            detail="Resume type not found.",
        )

    resume_path = RESUME_FILES[
        role_type
    ]

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
            application_row_to_dict(
                row
            )
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
    if is_blocked_company(
        application.company
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Applications to this "
                "company are blocked."
            ),
        )

    resume_path = RESUME_FILES.get(
        application.role_type
    )

    if resume_path is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "No resume is configured "
                "for this role type."
            ),
        )

    if not resume_path.exists():
        raise HTTPException(
            status_code=500,
            detail=(
                "The selected resume file "
                "is missing."
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
                    job_url,
                    remote_eligibility
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
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
                        application
                        .requires_human_review
                    ),
                    applied_at,
                    application.job_url,
                    application
                    .remote_eligibility,
                ),
            )

            connection.commit()

            application_id = cursor.lastrowid

    except sqlite3.IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail=(
                "This job is already "
                "in your application tracker."
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
            "remote_eligibility": (
                application.remote_eligibility
            ),
        }
    }


@app.patch(
    "/applications/{application_id}"
)
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
            (
                application_id,
            ),
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
            (
                application_id,
            ),
        ).fetchone()

    return {
        "application": application_row_to_dict(
            updated_row
        )
    }


@app.delete(
    "/applications/{application_id}"
)
def delete_application(
    application_id: int,
):
    with get_database_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM applications
            WHERE id = ?
            """,
            (
                application_id,
            ),
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