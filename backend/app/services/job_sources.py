from datetime import datetime, timezone
from html import unescape
import re

import requests


ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"


AI_TITLE_KEYWORDS = [
    "ai engineer",
    "artificial intelligence engineer",
    "machine learning engineer",
    "ml engineer",
    "llm engineer",
    "generative ai",
    "genai",
    "ai developer",
    "ai automation",
    "ai specialist",
    "ai associate",
    "prompt engineer",
    "nlp engineer",
    "agentic ai",
    "ai agent",
    "machine learning",
]


BDM_TITLE_KEYWORDS = [
    "business development manager",
    "business development executive",
    "business development representative",
    "business development",
    "bdm",
    "us it recruiter",
    "us recruiter",
    "technical recruiter",
    "it recruiter",
    "staffing recruiter",
    "recruitment manager",
    "resource development manager",
    "bench sales",
    "bench sales recruiter",
    "staffing manager",
    "account manager staffing",
]


AI_DESCRIPTION_KEYWORDS = [
    "large language model",
    "llm",
    "machine learning",
    "artificial intelligence",
    "generative ai",
    "genai",
    "prompt engineering",
    "agentic ai",
    "ai agents",
    "natural language processing",
    "nlp",
    "langchain",
    "openai",
    "anthropic",
    "claude",
]


BDM_DESCRIPTION_KEYWORDS = [
    "us staffing",
    "us it staffing",
    "us recruitment",
    "us it recruitment",
    "technical recruitment",
    "technical recruiting",
    "w2",
    "c2c",
    "1099",
    "bench sales",
    "consultant marketing",
    "vendor management",
    "staffing clients",
    "staffing business",
    "candidate sourcing",
    "full-cycle recruitment",
]


REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "work-from-home",
    "wfh",
    "distributed team",
    "fully remote",
]


WORLDWIDE_KEYWORDS = [
    "worldwide",
    "work from anywhere",
    "anywhere in the world",
    "globally remote",
    "global remote",
    "remote worldwide",
]


INDIA_KEYWORDS = [
    "india",
    "remote india",
    "india remote",
    "based in india",
]


EU_UK_KEYWORDS = [
    "eu/uk",
    "eu or uk",
    "europe only",
    "anywhere in europe",
    "based in europe",
    "within europe",
    "european union",
    "uk only",
    "united kingdom only",
]


US_ONLY_KEYWORDS = [
    "us only",
    "u.s. only",
    "united states only",
    "must be based in the us",
    "must be based in the united states",
    "remote within the us",
    "remote in the us",
]


EMEA_KEYWORDS = [
    "emea",
    "europe middle east and africa",
]


def strip_html(value: str) -> str:
    if not value:
        return ""

    text = re.sub(
        r"<script.*?>.*?</script>",
        " ",
        value,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<style.*?>.*?</style>",
        " ",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    text = re.sub(
        r"<[^>]+>",
        " ",
        text,
    )

    text = unescape(text)

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def classify_job(
    title: str,
    description: str,
    tags=None,
):
    tags = tags or []

    clean_title = (title or "").lower().strip()

    clean_description = strip_html(
        description or ""
    ).lower()

    tag_text = " ".join(tags).lower()

    title_ai_score = sum(
        5
        for keyword in AI_TITLE_KEYWORDS
        if keyword in clean_title
    )

    title_bdm_score = sum(
        5
        for keyword in BDM_TITLE_KEYWORDS
        if keyword in clean_title
    )

    description_ai_score = sum(
        1
        for keyword in AI_DESCRIPTION_KEYWORDS
        if keyword in clean_description
    )

    description_bdm_score = sum(
        1
        for keyword in BDM_DESCRIPTION_KEYWORDS
        if keyword in clean_description
    )

    tag_ai_score = sum(
        1
        for keyword in AI_TITLE_KEYWORDS
        if keyword in tag_text
    )

    tag_bdm_score = sum(
        1
        for keyword in BDM_TITLE_KEYWORDS
        if keyword in tag_text
    )

    ai_score = (
        title_ai_score
        + description_ai_score
        + tag_ai_score
    )

    bdm_score = (
        title_bdm_score
        + description_bdm_score
        + tag_bdm_score
    )

    if ai_score < 2 and bdm_score < 2:
        return None

    if ai_score > bdm_score:
        return "AI"

    if bdm_score > ai_score:
        return "US IT Recruiter"

    if title_ai_score > 0:
        return "AI"

    if title_bdm_score > 0:
        return "US IT Recruiter"

    return None


def detect_remote(
    api_remote: bool,
    title: str,
    location: str,
    description: str,
):
    if api_remote:
        return True

    searchable_text = " ".join(
        [
            title or "",
            location or "",
            description[:1500] if description else "",
        ]
    ).lower()

    return any(
        keyword in searchable_text
        for keyword in REMOTE_KEYWORDS
    )


def detect_remote_eligibility(
    title: str,
    location: str,
    description: str,
):
    searchable_text = " ".join(
        [
            title or "",
            location or "",
            description[:3000] if description else "",
        ]
    ).lower()

    if any(
        keyword in searchable_text
        for keyword in WORLDWIDE_KEYWORDS
    ):
        return "Worldwide"

    if any(
        keyword in searchable_text
        for keyword in INDIA_KEYWORDS
    ):
        return "India"

    if any(
        keyword in searchable_text
        for keyword in US_ONLY_KEYWORDS
    ):
        return "US only"

    if any(
        keyword in searchable_text
        for keyword in EU_UK_KEYWORDS
    ):
        return "EU/UK only"

    if any(
        keyword in searchable_text
        for keyword in EMEA_KEYWORDS
    ):
        return "EMEA"

    return "Unknown"


def format_posted_date(created_at):
    if not created_at:
        return "Recently posted"

    try:
        created_datetime = datetime.fromtimestamp(
            int(created_at),
            tz=timezone.utc,
        )

        now = datetime.now(timezone.utc)

        difference = now - created_datetime

        hours = int(
            difference.total_seconds() // 3600
        )

        if hours < 0:
            return "Recently posted"

        if hours < 1:
            return "Posted recently"

        if hours < 24:
            return f"Posted {hours}h ago"

        days = hours // 24

        if days == 1:
            return "Posted 1 day ago"

        return f"Posted {days} days ago"

    except (
        TypeError,
        ValueError,
        OSError,
    ):
        return "Recently posted"


def normalize_arbeitnow_job(job):
    title = (
        job.get("title")
        or ""
    ).strip()

    raw_description = (
        job.get("description")
        or ""
    )

    clean_description = strip_html(
        raw_description
    )

    role_type = classify_job(
        title=title,
        description=clean_description,
        tags=job.get("tags", []),
    )

    if role_type is None:
        return None

    slug = (
        job.get("slug")
        or ""
    )

    company = (
        job.get("company_name")
        or "Unknown company"
    ).strip()

    location = (
        job.get("location")
        or "Not specified"
    ).strip()

    job_types = (
        job.get("job_types")
        or []
    )

    remote = detect_remote(
        api_remote=bool(
            job.get("remote", False)
        ),
        title=title,
        location=location,
        description=clean_description,
    )

    remote_eligibility = (
        detect_remote_eligibility(
            title=title,
            location=location,
            description=clean_description,
        )
        if remote
        else "Not remote"
    )

    requires_human_review = (
        remote
        and remote_eligibility == "Unknown"
    )

    return {
        "external_id": (
            f"arbeitnow:{slug}"
        ),
        "role_type": role_type,
        "title": title,
        "company": company,
        "source": "Arbeitnow",
        "posted": format_posted_date(
            job.get("created_at")
        ),
        "created_at": (
            job.get("created_at")
        ),
        "location": location,
        "work_mode": (
            "Remote"
            if remote
            else "On-site / Hybrid"
        ),
        "remote": remote,
        "remote_eligibility": remote_eligibility,
        "experience": (
            ", ".join(job_types)
            if job_types
            else "Not specified"
        ),
        "description": (
            clean_description[:1200]
        ),
        "full_description": (
            clean_description
        ),
        "tags": (
            job.get("tags")
            or []
        ),
        "job_url": (
            job.get("url")
            or ""
        ),
        "requires_human_review": (
            requires_human_review
        ),
    }


def fetch_arbeitnow_jobs(
    pages: int = 2,
):
    jobs = []

    pages = max(
        1,
        min(pages, 5),
    )

    for page in range(
        1,
        pages + 1,
    ):
        response = requests.get(
            ARBEITNOW_API_URL,
            params={
                "page": page,
            },
            timeout=20,
            headers={
                "User-Agent": (
                    "Roleza/1.0 Job Search Assistant"
                )
            },
        )

        response.raise_for_status()

        payload = response.json()

        raw_jobs = payload.get(
            "data",
            [],
        )

        for raw_job in raw_jobs:
            normalized_job = (
                normalize_arbeitnow_job(
                    raw_job
                )
            )

            if normalized_job is None:
                continue

            jobs.append(
                normalized_job
            )

        links = payload.get(
            "links",
            {},
        )

        if not links.get("next"):
            break

    return jobs