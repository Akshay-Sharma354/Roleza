from datetime import datetime, timezone
import requests

from app.services.job_sources import (
    strip_html,
    classify_job,
    detect_remote,
    detect_remote_eligibility,
)


LEVER_API_BASE = "https://api.lever.co/v0/postings"


LEVER_COMPANIES = {
    "Jobgether": "jobgether",
    "Level AI": "levelai",
    "Anlatan": "Anlatan",
    "Artera": "artera",
    "BLEN": "blencorp",
}


def format_posted_date(timestamp_ms):
    if not timestamp_ms:
        return "Recently posted"

    try:
        timestamp_seconds = int(timestamp_ms) / 1000

        posted = datetime.fromtimestamp(
            timestamp_seconds,
            tz=timezone.utc,
        )

        now = datetime.now(timezone.utc)

        hours = int(
            (now - posted).total_seconds()
            // 3600
        )

        if hours < 1:
            return "Posted recently"

        if hours < 24:
            return f"Posted {hours}h ago"

        days = hours // 24

        if days == 1:
            return "Posted 1 day ago"

        return f"Posted {days} days ago"

    except Exception:
        return "Recently posted"


def build_description(job):
    parts = []

    description = job.get("descriptionPlain")

    if description:
        parts.append(description)

    for item in job.get("lists", []):
        heading = item.get("text", "")
        content = strip_html(
            item.get("content", "")
        )

        if heading:
            parts.append(heading)

        if content:
            parts.append(content)

    additional = strip_html(
        job.get("additional", "")
    )

    if additional:
        parts.append(additional)

    return "\n".join(parts).strip()


def normalize_lever_job(
    job,
    company_name,
    company_slug,
):
    title = (
        job.get("text")
        or ""
    ).strip()

    description = build_description(job)

    role_type = classify_job(
        title=title,
        description=description,
        tags=[],
    )

    if role_type is None:
        return None

    categories = (
        job.get("categories")
        or {}
    )

    location = (
        categories.get("location")
        or "Not specified"
    )

    workplace_type = (
        job.get("workplaceType")
        or ""
    ).lower()

    api_remote = (
        workplace_type == "remote"
    )

    remote = detect_remote(
        api_remote=api_remote,
        title=title,
        location=location,
        description=description,
    )

    remote_eligibility = (
        detect_remote_eligibility(
            title=title,
            location=location,
            description=description,
        )
        if remote
        else "Not remote"
    )

    created_at = (
        job.get("createdAt")
        or 0
    )

    job_id = str(
        job.get("id")
        or ""
    )

    if not job_id:
        return None

    job_url = (
        job.get("hostedUrl")
        or job.get("applyUrl")
        or ""
    )

    commitment = (
        categories.get("commitment")
        or "Not specified"
    )

    requires_human_review = (
        remote
        and remote_eligibility == "Unknown"
    )

    return {
        "external_id": (
            f"lever:{company_slug}:{job_id}"
        ),
        "role_type": role_type,
        "title": title,
        "company": company_name,
        "source": "Lever",
        "posted": format_posted_date(
            created_at
        ),
        "created_at": (
            int(created_at / 1000)
            if created_at
            else 0
        ),
        "location": location,
        "work_mode": (
            "Remote"
            if remote
            else "On-site / Hybrid"
        ),
        "remote": remote,
        "remote_eligibility": (
            remote_eligibility
        ),
        "experience": commitment,
        "description": description[:1200],
        "full_description": description,
        "tags": [],
        "job_url": job_url,
        "requires_human_review": (
            requires_human_review
        ),
    }


def fetch_lever_company(
    company_name,
    company_slug,
):
    url = (
        f"{LEVER_API_BASE}/"
        f"{company_slug}"
    )

    response = requests.get(
        url,
        params={
            "mode": "json",
        },
        timeout=20,
        headers={
            "User-Agent":
                "Roleza/1.0 Job Search Assistant"
        },
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(payload, list):
        return []

    jobs = []

    for raw_job in payload:
        normalized = normalize_lever_job(
            raw_job,
            company_name,
            company_slug,
        )

        if normalized is not None:
            jobs.append(normalized)

    return jobs


def fetch_lever_jobs():
    jobs = []
    errors = []

    for company_name, company_slug in (
        LEVER_COMPANIES.items()
    ):
        try:
            company_jobs = fetch_lever_company(
                company_name,
                company_slug,
            )

            jobs.extend(company_jobs)

        except requests.RequestException as error:
            errors.append(
                f"{company_name}: {error}"
            )

    return {
        "jobs": jobs,
        "errors": errors,
    }
