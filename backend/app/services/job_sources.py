from datetime import datetime, timezone
from html import unescape
import re

import requests


ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"
REMOTEOK_API_URL = "https://remoteok.com/api"


AI_TITLE_KEYWORDS = [
    "ai engineer",
    "artificial intelligence engineer",
    "machine learning engineer",
    "ml engineer",
    "llm engineer",
    "generative ai engineer",
    "genai engineer",
    "ai developer",
    "ai automation engineer",
    "ai specialist",
    "ai associate",
    "prompt engineer",
    "nlp engineer",
    "agentic ai engineer",
    "applied ai engineer",
    "ai researcher",
    "applied ai researcher",
    "ai research engineer",
    "machine learning researcher",
    "machine learning scientist",
    "ai scientist",
    "research scientist ai",
    "data scientist",
    "machine learning",
    "forward deployed engineer",
]


BDM_TITLE_KEYWORDS = [
    "business development manager",
    "business development executive",
    "business development representative",
    "business development associate",
    "business development specialist",
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


AI_CONTEXT_KEYWORDS = [
    "large language model",
    "llm",
    "machine learning",
    "artificial intelligence",
    "generative ai",
    "genai",
    "prompt engineering",
    "agentic ai",
    "ai agent",
    "ai agents",
    "natural language processing",
    "nlp",
    "langchain",
    "openai",
    "anthropic",
    "claude",
    "rag",
    "retrieval augmented generation",
    "mcp",
    "vector database",
    "model orchestration",
    "foundation model",
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
    "globally distributed",
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
    "remote - europe",
    "remote europe",
]


US_ONLY_KEYWORDS = [
    "us only",
    "u.s. only",
    "united states only",
    "must be based in the us",
    "must be based in the united states",
    "remote within the us",
    "remote in the us",
    "remote us",
    "remote usa",
    "remote - us",
    "remote - usa",
    "us remote",
    "usa remote",
    "united states (remote)",
    "remote, united states",
    "remote united states",
]


US_RESTRICTION_KEYWORDS = [
    "us citizenship required",
    "u.s. citizenship required",
    "us citizenship is required",
    "u.s. citizenship is required",
    "must be a us citizen",
    "must be a u.s. citizen",
    "green card required",
    "greencard required",
    "us citizen or green card",
    "us citizen or greencard",
    "authorized to work in the united states",
    "authorized to work in the us",
    "authorization to work in the united states",
    "authorization to work in the us",
]


EMEA_KEYWORDS = [
    "emea",
    "europe middle east and africa",
]


GENERIC_ABOUT_WORDS = {
    "us",
    "the",
    "role",
    "team",
    "company",
    "position",
    "opportunity",
    "job",
    "you",
}


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


def normalize_text(value: str) -> str:
    value = (
        value
        or ""
    ).lower()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def contains_keyword(
    text: str,
    keywords,
) -> bool:
    clean_text = (
        text
        or ""
    ).lower().strip()

    return any(
        keyword in clean_text
        for keyword in keywords
    )


def has_ai_context(
    description: str,
) -> bool:
    clean_description = strip_html(
        description or ""
    ).lower()

    return any(
        keyword in clean_description
        for keyword in AI_CONTEXT_KEYWORDS
    )


def classify_job(
    title: str,
    description: str,
    tags=None,
):
    """
    Strict title-first classifier.

    A description mentioning AI is not
    enough to turn an unrelated job into
    an AI job.
    """

    clean_title = (
        title
        or ""
    ).lower().strip()

    if contains_keyword(
        clean_title,
        BDM_TITLE_KEYWORDS,
    ):
        return "US IT Recruiter"

    if contains_keyword(
        clean_title,
        AI_TITLE_KEYWORDS,
    ):
        if (
            "forward deployed engineer"
            in clean_title
            and not has_ai_context(
                description
            )
        ):
            return None

        return "AI"

    return None


def classify_remoteok_job(
    title: str,
    description: str,
    tags=None,
):
    return classify_job(
        title=title,
        description=description,
        tags=tags,
    )


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
            (
                description[:1500]
                if description
                else ""
            ),
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
    title_location = " ".join(
        [
            title or "",
            location or "",
        ]
    ).lower()

    searchable_text = " ".join(
        [
            title or "",
            location or "",
            (
                description[:4000]
                if description
                else ""
            ),
        ]
    ).lower()

    # Explicit location restrictions
    # should beat generic phrases like
    # "work from anywhere" in benefits.
    if any(
        keyword in title_location
        for keyword in US_ONLY_KEYWORDS
    ):
        return "US only"

    if any(
        keyword in title_location
        for keyword in EU_UK_KEYWORDS
    ):
        return "EU/UK only"

    if any(
        keyword in title_location
        for keyword in EMEA_KEYWORDS
    ):
        return "EMEA"

    if any(
        keyword in searchable_text
        for keyword in US_RESTRICTION_KEYWORDS
    ):
        return "US only"

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

    if any(
        keyword in searchable_text
        for keyword in INDIA_KEYWORDS
    ):
        return "India"

    if any(
        keyword in searchable_text
        for keyword in WORLDWIDE_KEYWORDS
    ):
        return "Worldwide"

    return "Unknown"


def extract_about_company(
    description: str,
):
    """
    Detect obvious descriptions that
    begin with something like:

    "About Waniwani Waniwani builds..."

    This is only used as a conservative
    source-quality check.
    """

    if not description:
        return None

    start = (
        description
        .strip()[:250]
    )

    match = re.match(
        r"(?i)^about\s+([a-z0-9][a-z0-9&.\-_]{1,40})\b",
        start,
    )

    if not match:
        return None

    candidate = (
        match.group(1)
        .strip()
        .lower()
    )

    if candidate in GENERIC_ABOUT_WORDS:
        return None

    return candidate


def arbeitnow_identity_conflict(
    company: str,
    description: str,
) -> bool:
    """
    Reject only an obvious mismatch.

    Example:
    company_name = Hexa
    description begins "About Waniwani..."

    We do not attempt to repair the job.
    We simply avoid presenting uncertain
    upstream data to the user.
    """

    described_company = (
        extract_about_company(
            description
        )
    )

    if not described_company:
        return False

    normalized_company = normalize_text(
        company
    )

    normalized_described_company = (
        normalize_text(
            described_company
        )
    )

    if not normalized_company:
        return False

    if (
        normalized_described_company
        in normalized_company
    ):
        return False

    first_company_word = (
        normalized_company.split()[0]
        if normalized_company.split()
        else ""
    )

    if (
        normalized_described_company
        == first_company_word
    ):
        return False

    return True


def format_posted_date(
    created_at,
):
    if not created_at:
        return "Recently posted"

    try:
        created_datetime = (
            datetime.fromtimestamp(
                int(created_at),
                tz=timezone.utc,
            )
        )

        now = datetime.now(
            timezone.utc
        )

        difference = (
            now
            - created_datetime
        )

        hours = int(
            difference.total_seconds()
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

        days = hours // 24

        if days == 1:
            return "Posted 1 day ago"

        return (
            f"Posted {days} days ago"
        )

    except (
        TypeError,
        ValueError,
        OSError,
    ):
        return "Recently posted"


def normalize_arbeitnow_job(
    job,
):
    title = (
        job.get("title")
        or ""
    ).strip()

    company = (
        job.get("company_name")
        or "Unknown company"
    ).strip()

    raw_description = (
        job.get("description")
        or ""
    )

    clean_description = strip_html(
        raw_description
    )

    # Protect Roleza from clearly
    # inconsistent upstream listings.
    if arbeitnow_identity_conflict(
        company=company,
        description=clean_description,
    ):
        return None

    role_type = classify_job(
        title=title,
        description=clean_description,
        tags=job.get(
            "tags",
            [],
        ),
    )

    if role_type is None:
        return None

    slug = (
        job.get("slug")
        or ""
    ).strip()

    if not slug:
        return None

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
            job.get(
                "remote",
                False,
            )
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
        and remote_eligibility
        == "Unknown"
    )

    return {
        "external_id":
            f"arbeitnow:{slug}",

        "role_type":
            role_type,

        "title":
            title,

        "company":
            company,

        "source":
            "Arbeitnow",

        "posted":
            format_posted_date(
                job.get("created_at")
            ),

        "created_at":
            job.get("created_at"),

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
            (
                ", ".join(job_types)
                if job_types
                else "Not specified"
            ),

        "description":
            clean_description[:1200],

        "full_description":
            clean_description,

        "tags":
            job.get("tags")
            or [],

        "job_url":
            job.get("url")
            or "",

        "requires_human_review":
            requires_human_review,
    }


def fetch_arbeitnow_jobs(
    pages: int = 2,
):
    jobs = []

    pages = max(
        1,
        min(
            pages,
            5,
        ),
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
                "User-Agent":
                    "Roleza/1.0 Job Search Assistant"
            },
        )

        response.raise_for_status()

        payload = response.json()

        for raw_job in payload.get(
            "data",
            [],
        ):
            normalized_job = (
                normalize_arbeitnow_job(
                    raw_job
                )
            )

            if (
                normalized_job
                is not None
            ):
                jobs.append(
                    normalized_job
                )

        links = payload.get(
            "links",
            {},
        )

        if not links.get(
            "next"
        ):
            break

    return jobs


def normalize_remoteok_job(
    job,
):
    remoteok_id = str(
        job.get("id")
        or ""
    ).strip()

    if not remoteok_id:
        return None

    title = (
        job.get("position")
        or ""
    ).strip()

    company = (
        job.get("company")
        or "Unknown company"
    ).strip()

    location = (
        job.get("location")
        or "Remote"
    ).strip()

    raw_description = (
        job.get("description")
        or ""
    )

    clean_description = strip_html(
        raw_description
    )

    tags = (
        job.get("tags")
        or []
    )

    role_type = (
        classify_remoteok_job(
            title=title,
            description=clean_description,
            tags=tags,
        )
    )

    if role_type is None:
        return None

    description_lower = (
        clean_description.lower()
    )

    obvious_not_remote = any(
        phrase
        in description_lower
        for phrase in [
            "there is no option to work remotely",
            "work must be completed at the physical location",
            "on-site only",
            "onsite only",
        ]
    )

    if obvious_not_remote:
        return None

    remote_eligibility = (
        detect_remote_eligibility(
            title=title,
            location=location,
            description=clean_description,
        )
    )

    requires_human_review = (
        remote_eligibility
        == "Unknown"
    )

    created_at = (
        job.get("epoch")
        or 0
    )

    job_url = (
        job.get("apply_url")
        or job.get("url")
        or ""
    )

    salary_min = (
        job.get("salary_min")
        or 0
    )

    salary_max = (
        job.get("salary_max")
        or 0
    )

    if (
        salary_min
        and salary_max
    ):
        experience = (
            f"${salary_min:,} - "
            f"${salary_max:,}"
        )

    elif salary_min:
        experience = (
            f"From ${salary_min:,}"
        )

    elif salary_max:
        experience = (
            f"Up to ${salary_max:,}"
        )

    else:
        experience = (
            "Not specified"
        )

    return {
        "external_id":
            f"remoteok:{remoteok_id}",

        "role_type":
            role_type,

        "title":
            title,

        "company":
            company,

        "source":
            "Remote OK",

        "posted":
            format_posted_date(
                created_at
            ),

        "created_at":
            created_at,

        "location":
            location or "Remote",

        "work_mode":
            "Remote",

        "remote":
            True,

        "remote_eligibility":
            remote_eligibility,

        "experience":
            experience,

        "description":
            clean_description[:1200],

        "full_description":
            clean_description,

        "tags":
            tags,

        "job_url":
            job_url,

        "requires_human_review":
            requires_human_review,
    }


def fetch_remoteok_jobs():
    response = requests.get(
        REMOTEOK_API_URL,
        timeout=20,
        headers={
            "User-Agent":
                "Roleza/1.0 Job Search Assistant"
        },
    )

    response.raise_for_status()

    payload = response.json()

    if not isinstance(
        payload,
        list,
    ):
        return []

    jobs = []

    # Remote OK's first object is
    # normally API metadata.
    for raw_job in payload[1:]:
        if not isinstance(
            raw_job,
            dict,
        ):
            continue

        normalized_job = (
            normalize_remoteok_job(
                raw_job
            )
        )

        if normalized_job is not None:
            jobs.append(
                normalized_job
            )

    return jobs


def normalize_dedupe_text(
    value: str,
) -> str:
    return normalize_text(
        value
    )


def deduplicate_jobs(
    jobs,
):
    unique_jobs = []
    seen = set()

    for job in jobs:
        title = (
            normalize_dedupe_text(
                job.get("title")
            )
        )

        company = (
            normalize_dedupe_text(
                job.get("company")
            )
        )

        if (
            not title
            or not company
        ):
            continue

        key = (
            title,
            company,
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        unique_jobs.append(
            job
        )

    return unique_jobs


def fetch_all_live_jobs():
    from app.services.greenhouse import (
        fetch_greenhouse_jobs,
    )

    from app.services.company_sources import (
        fetch_company_watchlist_jobs,
    )

    all_jobs = []
    source_errors = []

    try:
        all_jobs.extend(
            fetch_arbeitnow_jobs(
                pages=2
            )
        )

    except requests.RequestException as error:
        source_errors.append(
            f"Arbeitnow: {error}"
        )

    except Exception as error:
        source_errors.append(
            f"Arbeitnow: {error}"
        )

    try:
        all_jobs.extend(
            fetch_remoteok_jobs()
        )

    except requests.RequestException as error:
        source_errors.append(
            f"Remote OK: {error}"
        )

    except Exception as error:
        source_errors.append(
            f"Remote OK: {error}"
        )

    try:
        greenhouse_result = (
            fetch_greenhouse_jobs()
        )

        all_jobs.extend(
            greenhouse_result.get(
                "jobs",
                [],
            )
        )

        for error in (
            greenhouse_result.get(
                "errors",
                [],
            )
        ):
            source_errors.append(
                f"Greenhouse: {error}"
            )

    except Exception as error:
        source_errors.append(
            f"Greenhouse: {error}"
        )

    try:
        company_result = (
            fetch_company_watchlist_jobs()
        )

        all_jobs.extend(
            company_result.get(
                "jobs",
                [],
            )
        )

        for error in (
            company_result.get(
                "errors",
                [],
            )
        ):
            source_errors.append(
                f"Company Watchlist: {error}"
            )

    except Exception as error:
        source_errors.append(
            f"Company Watchlist: {error}"
        )

    jobs = deduplicate_jobs(
        all_jobs
    )

    jobs.sort(
        key=lambda item: (
            item.get(
                "created_at"
            )
            or 0
        ),
        reverse=True,
    )

    return {
        "jobs": jobs,

        "source_errors":
            source_errors,

        "sources": [
            "Arbeitnow",
            "Remote OK",
            "Greenhouse",
            "Company Watchlist",
        ],
    }