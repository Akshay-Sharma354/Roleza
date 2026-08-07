from datetime import datetime, timezone
from html import unescape

import requests

from app.services.job_sources import (
    strip_html,
    classify_job,
    detect_remote,
    detect_remote_eligibility,
)


GREENHOUSE_API_BASE = (
    "https://boards-api.greenhouse.io/v1/boards"
)


GREENHOUSE_BOARDS = {
    "Particle41": "particle41llc",
    "Remote": "remotecom",
    "Sezzle": "sezzle",
    "AlphaSense": "alphasense",
    "Yurts": "yurtsai",
    "You.com": "youcom",
    "Snorkel AI": "snorkelai",
}


def clean_greenhouse_content(
    value: str,
) -> str:
    """
    Greenhouse sometimes returns HTML
    inside escaped HTML.

    Example:
    &lt;div&gt;About Company&lt;/div&gt;

    Decode first, then strip HTML.
    Run the cleaner twice as an extra
    safeguard against nested encoding.
    """

    if not value:
        return ""

    decoded = unescape(
        value
    )

    cleaned = strip_html(
        decoded
    )

    cleaned_again = strip_html(
        cleaned
    )

    return cleaned_again.strip()


def parse_greenhouse_date(
    value,
):
    if not value:
        return 0

    try:
        dt = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )

        return int(
            dt.timestamp()
        )

    except Exception:
        return 0


def format_posted_date(
    timestamp,
):
    if not timestamp:
        return "Recently posted"

    now = datetime.now(
        timezone.utc
    )

    posted = datetime.fromtimestamp(
        timestamp,
        tz=timezone.utc,
    )

    hours = int(
        (
            now
            - posted
        ).total_seconds()
        // 3600
    )

    if hours < 0:
        return "Recently posted"

    if hours < 1:
        return "Posted recently"

    if hours < 24:
        return (
            f"Posted {hours}h ago"
        )

    days = (
        hours // 24
    )

    if days == 1:
        return "Posted 1 day ago"

    return (
        f"Posted {days} days ago"
    )


def normalize_greenhouse_job(
    job,
    company_name,
    board_token,
):
    title = (
        job.get("title")
        or ""
    ).strip()

    raw_content = (
        job.get("content")
        or ""
    )

    content = (
        clean_greenhouse_content(
            raw_content
        )
    )

    role_type = classify_job(
        title=title,
        description=content,
        tags=[],
    )

    if role_type is None:
        return None

    location_data = (
        job.get("location")
        or {}
    )

    location = (
        location_data.get("name")
        or "Not specified"
    ).strip()

    remote = detect_remote(
        api_remote=False,
        title=title,
        location=location,
        description=content,
    )

    remote_eligibility = (
        detect_remote_eligibility(
            title=title,
            location=location,
            description=content,
        )
        if remote
        else "Not remote"
    )

    updated_at = (
        parse_greenhouse_date(
            job.get("updated_at")
        )
    )

    job_id = str(
        job.get("id")
        or ""
    ).strip()

    if not job_id:
        return None

    absolute_url = (
        job.get("absolute_url")
        or ""
    ).strip()

    requires_human_review = (
        remote
        and remote_eligibility
        == "Unknown"
    )

    return {
        "external_id": (
            f"greenhouse:"
            f"{board_token}:"
            f"{job_id}"
        ),

        "role_type":
            role_type,

        "title":
            title,

        "company":
            company_name,

        "source":
            "Greenhouse",

        "posted":
            format_posted_date(
                updated_at
            ),

        "created_at":
            updated_at,

        "location":
            location,

        "work_mode":
            (
                "Remote"
                if remote
                else "On-site / Hybrid"
            ),

        "remote":
            remote,

        "remote_eligibility":
            remote_eligibility,

        "experience":
            "Not specified",

        "description":
            content[:1200],

        "full_description":
            content,

        "tags":
            [],

        "job_url":
            absolute_url,

        "requires_human_review":
            requires_human_review,
    }


def fetch_greenhouse_board(
    company_name,
    board_token,
):
    url = (
        f"{GREENHOUSE_API_BASE}/"
        f"{board_token}/jobs"
    )

    response = requests.get(
        url,
        params={
            "content": "true",
        },
        timeout=20,
        headers={
            "User-Agent":
                "Roleza/1.0 Job Search Assistant"
        },
    )

    response.raise_for_status()

    payload = response.json()

    jobs = []

    for raw_job in payload.get(
        "jobs",
        [],
    ):
        normalized = (
            normalize_greenhouse_job(
                raw_job,
                company_name,
                board_token,
            )
        )

        if normalized is not None:
            jobs.append(
                normalized
            )

    return jobs


def fetch_greenhouse_jobs():
    jobs = []
    errors = []

    for company_name, board_token in (
        GREENHOUSE_BOARDS.items()
    ):
        try:
            company_jobs = (
                fetch_greenhouse_board(
                    company_name,
                    board_token,
                )
            )

            jobs.extend(
                company_jobs
            )

        except requests.RequestException as error:
            errors.append(
                f"{company_name}: {error}"
            )

        except Exception as error:
            errors.append(
                f"{company_name}: {error}"
            )

    return {
        "jobs": jobs,
        "errors": errors,
    }