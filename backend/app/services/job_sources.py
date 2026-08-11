from datetime import datetime, timezone
from html import unescape
from urllib.parse import quote_plus
import re

import requests


ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"
REMOTEOK_API_URL = "https://remoteok.com/api"


# =========================================================
# TARGET SEARCH STRATEGY
# =========================================================

AI_SEARCH_QUERIES = [
    "Claude Code Operator",
    "AI Operator",
    "AI Automation Specialist",
    "AI Automation Engineer",
    "AI Workflow Specialist",
    "Prompt Engineer",
    "Prompt Engineering Specialist",
    "AI Agent Engineer",
    "Junior AI Agent Engineer",
    "Agentic AI Engineer",
    "LLM Application Engineer",
    "LLM Engineer",
    "Generative AI Specialist",
    "AI Implementation Specialist",
    "AI Integration Engineer",
    "AI Solutions Engineer",
    "AI Technical Specialist",
    "AI Technical Consultant",
    "AI Product Specialist",
    "AI Automation Generalist",
    "AI Native Builder",
    "AI Systems Builder",
    "AI Evaluation Specialist",
    "AI Testing Engineer",
    "LLM Trainer",
    "AI Trainer",
    "Junior AI Engineer",
    "Associate AI Engineer",
]

BDM_SEARCH_QUERIES = [
    "US IT Recruiter",
    "Technical Recruiter",
    "IT Recruiter",
    "Senior Technical Recruiter",
    "Talent Acquisition Specialist",
    "Talent Acquisition Executive",
    "Talent Acquisition Lead",
    "Recruitment Manager",
    "Staffing Recruiter",
    "US Staffing Recruiter",
    "Bench Sales Recruiter",
    "Resource Development Manager",
    "Delivery Manager Staffing",
    "Recruitment Business Development",
    "Staffing Business Development",
    "BDM US Staffing",
]

TARGET_LOCATIONS = [
    "Remote",
    "Remote India",
    "Noida",
    "Gurgaon",
    "Gurugram",
    "Delhi",
    "Delhi NCR",
]


AI_TITLE_KEYWORDS = [
    "claude code operator",
    "claude operator",
    "ai operator",
    "ai engineer",
    "artificial intelligence engineer",
    "machine learning engineer",
    "ml engineer",
    "llm engineer",
    "llm application engineer",
    "generative ai engineer",
    "genai engineer",
    "ai developer",
    "ai automation engineer",
    "ai automation specialist",
    "ai automation generalist",
    "ai workflow specialist",
    "ai workflow engineer",
    "ai specialist",
    "ai associate",
    "prompt engineer",
    "prompt engineering specialist",
    "ai agent engineer",
    "junior ai agent engineer",
    "agentic ai engineer",
    "ai agent builder",
    "ai native builder",
    "ai systems builder",
    "ai implementation specialist",
    "ai integration engineer",
    "ai solutions engineer",
    "ai technical specialist",
    "ai technical consultant",
    "ai product specialist",
    "ai evaluation specialist",
    "ai testing engineer",
    "llm trainer",
    "ai trainer",
    "nlp engineer",
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
    "us staffing recruiter",
    "recruitment manager",
    "talent acquisition specialist",
    "talent acquisition executive",
    "talent acquisition lead",
    "resource development manager",
    "bench sales",
    "bench sales recruiter",
    "staffing manager",
    "delivery manager staffing",
    "account manager staffing",
    "recruitment business development",
    "staffing business development",
]

AI_CONTEXT_KEYWORDS = [
    "claude",
    "claude code",
    "anthropic",
    "large language model",
    "large language models",
    "llm",
    "machine learning",
    "artificial intelligence",
    "generative ai",
    "genai",
    "prompt engineering",
    "prompt design",
    "agentic ai",
    "ai agent",
    "ai agents",
    "agent orchestration",
    "workflow automation",
    "ai workflow",
    "ai workflows",
    "automation",
    "natural language processing",
    "nlp",
    "langchain",
    "openai",
    "gpt",
    "rag",
    "retrieval augmented generation",
    "mcp",
    "vector database",
    "model orchestration",
    "foundation model",
    "fastapi",
    "python",
    "react",
    "api",
    "apis",
]

REMOTE_KEYWORDS = [
    "remote",
    "work from home",
    "work-from-home",
    "wfh",
    "distributed team",
    "fully remote",
    "remote first",
    "remote-first",
]

WORLDWIDE_KEYWORDS = [
    "worldwide",
    "work from anywhere",
    "anywhere in the world",
    "globally remote",
    "global remote",
    "remote worldwide",
    "globally distributed",
    "remote anywhere",
    "remote from anywhere",
    "anywhere globally",
    "anywhere worldwide",
    "open globally",
    "open worldwide",
    "candidates worldwide",
    "applicants worldwide",
    "global candidates",
    "hire globally",
    "hiring globally",
]

INDIA_KEYWORDS = [
    "india",
    "remote india",
    "india remote",
    "based in india",
    "located in india",
    "candidates in india",
    "candidates based in india",
    "open to candidates in india",
    "work remotely from india",
    "remote from india",
    "hiring in india",
    "india-based",
    "india based",
    "noida",
    "gurgaon",
    "gurugram",
    "delhi",
    "delhi ncr",
    "ncr",
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
    "united kingdom",
    "based in the united kingdom",
    "located in the united kingdom",
    "reside in the united kingdom",
    "live in the united kingdom",
    "living in the united kingdom",
    "candidates in the united kingdom",
    "candidates based in the united kingdom",
    "open to candidates in the united kingdom",
    "must live in the united kingdom",
    "must reside in the united kingdom",
    "must be based in the united kingdom",
    "based in the uk",
    "located in the uk",
    "reside in the uk",
    "live in the uk",
    "living in the uk",
    "candidates in the uk",
    "uk-based",
    "uk based",
    "based in european union",
    "based in the european union",
    "candidates in europe",
    "candidates based in europe",
    "must be based in europe",
    "europe-based",
    "europe based",
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
    "united states remote",
    "united states (remote)",
    "remote, united states",
    "remote united states",
    "candidates in the united states",
    "candidates based in the united states",
    "open to candidates in the united states",
    "must reside in the united states",
    "must live in the united states",
    "must be located in the united states",
    "us-based candidates",
    "us based candidates",
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
    "must be authorized to work in the united states",
    "must be authorized to work in the us",
]

EMEA_KEYWORDS = [
    "emea",
    "europe middle east and africa",
    "emea only",
    "remote emea",
    "remote - emea",
    "candidates in emea",
    "candidates based in emea",
    "must be based in emea",
]

RELOCATION_ONLY_KEYWORDS = [
    "relocation required",
    "must relocate",
    "willing to relocate",
    "relocate to",
    "onsite only",
    "on-site only",
    "work from office",
    "office based",
    "office-based",
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


# =========================================================
# HELPERS
# =========================================================

def now_epoch():
    return int(
        datetime.now(
            timezone.utc
        ).timestamp()
    )


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
    clean_title = (
        title
        or ""
    ).lower().strip()

    clean_description = (
        description
        or ""
    ).lower()

    clean_tags = " ".join(
        tags or []
    ).lower()

    combined = " ".join(
        [
            clean_title,
            clean_description[:4000],
            clean_tags,
        ]
    )

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
            "forward deployed engineer" in clean_title
            and not has_ai_context(description)
        ):
            return None

        return "AI"

    # Special case:
    # Some current AI jobs use titles like
    # "Operator", "Builder", "Automation Generalist".
    # We allow them only when the description
    # strongly mentions AI/Claude/LLMs.
    ai_soft_title_words = [
        "operator",
        "builder",
        "automation",
        "workflow",
        "implementation",
        "solutions",
        "technical specialist",
        "technical consultant",
        "product specialist",
        "testing",
        "evaluation",
        "trainer",
    ]

    if (
        any(word in clean_title for word in ai_soft_title_words)
        and has_ai_context(combined)
    ):
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
                description[:8000]
                if description
                else ""
            ),
        ]
    ).lower()

    if any(
        keyword in searchable_text
        for keyword in RELOCATION_ONLY_KEYWORDS
    ):
        return "Relocation / onsite"

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
        for keyword in US_ONLY_KEYWORDS + US_RESTRICTION_KEYWORDS
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


def format_posted_date(
    created_at,
):
    if not created_at:
        return "Recently posted"

    try:
        created_datetime = datetime.fromtimestamp(
            int(created_at),
            tz=timezone.utc,
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


def extract_about_company(
    description: str,
):
    if not description:
        return None

    start = description.strip()[:250]

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
    described_company = extract_about_company(
        description
    )

    if not described_company:
        return False

    normalized_company = normalize_text(
        company
    )

    normalized_described_company = normalize_text(
        described_company
    )

    if not normalized_company:
        return False

    if normalized_described_company in normalized_company:
        return False

    first_company_word = (
        normalized_company.split()[0]
        if normalized_company.split()
        else ""
    )

    if normalized_described_company == first_company_word:
        return False

    return True


# =========================================================
# CURATED INDIA JOB SEARCH SOURCES
# =========================================================

def build_indeed_url(
    query: str,
    location: str,
):
    return (
        "https://in.indeed.com/jobs"
        f"?q={quote_plus(query)}"
        f"&l={quote_plus(location)}"
        "&fromage=7"
        "&sort=date"
    )


def build_naukri_url(
    query: str,
    location: str,
):
    slug_query = (
        query.lower()
        .replace("/", " ")
        .replace("&", " ")
    )

    slug_query = re.sub(
        r"[^a-z0-9]+",
        "-",
        slug_query,
    ).strip("-")

    slug_location = (
        location.lower()
        .replace("/", " ")
        .replace("&", " ")
    )

    slug_location = re.sub(
        r"[^a-z0-9]+",
        "-",
        slug_location,
    ).strip("-")

    return (
        "https://www.naukri.com/"
        f"{slug_query}-jobs-in-{slug_location}"
    )


def build_linkedin_url(
    query: str,
    location: str,
):
    return (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={quote_plus(query)}"
        f"&location={quote_plus(location)}"
        "&f_TPR=r604800"
        "&sortBy=DD"
    )


def build_cutshort_url(
    query: str,
):
    return (
        "https://cutshort.io/jobs/"
        f"{quote_plus(query).replace('+', '-')}-jobs"
    )


def build_wellfound_url(
    query: str,
):
    return (
        "https://wellfound.com/jobs"
        f"?query={quote_plus(query)}"
    )


def create_search_card(
    source: str,
    role_type: str,
    query: str,
    location: str,
    url: str,
    source_priority: int,
):
    created_at = now_epoch()

    title = (
        f"{query} jobs"
    )

    company = (
        f"{source} Search"
    )

    if role_type == "AI":
        description = (
            f"Search {source} for fresh {query} roles in {location}. "
            "This is a high-priority Roleza search card for AI, Claude, "
            "Prompt Engineering, LLM, Agentic AI, and AI automation jobs. "
            "Open the job board, choose a real listing, and when it opens "
            "an external company or ATS page, use Roleza to inspect and "
            "prepare the application."
        )
    else:
        description = (
            f"Search {source} for fresh {query} roles in {location}. "
            "This is a high-priority Roleza search card for US IT Recruiting, "
            "Technical Recruiting, Staffing, BDM, Bench Sales, Talent Acquisition, "
            "and Resource Development roles in India, Remote India, Noida, "
            "Gurgaon, Gurugram, Delhi, and Delhi NCR."
        )

    remote = (
        "remote" in location.lower()
    )

    remote_eligibility = (
        "India"
        if (
            "india" in location.lower()
            or "noida" in location.lower()
            or "gurgaon" in location.lower()
            or "gurugram" in location.lower()
            or "delhi" in location.lower()
            or "ncr" in location.lower()
        )
        else "Unknown"
    )

    return {
        "external_id":
            f"search:{source}:{role_type}:{query}:{location}",

        "role_type":
            role_type,

        "title":
            title,

        "company":
            company,

        "source":
            source,

        "posted":
            "Search today",

        "created_at":
            created_at + source_priority,

        "location":
            location,

        "work_mode":
            (
                "Remote"
                if remote
                else "Search"
            ),

        "remote":
            True,

        "remote_eligibility":
            remote_eligibility,

        "experience":
            "Fresh search",

        "description":
            description[:1200],

        "full_description":
            description,

        "tags":
            [
                role_type,
                query,
                location,
                source,
                "India",
                "Roleza search card",
            ],

        "job_url":
            url,

        "requires_human_review":
            False,

        "is_search_card":
            True,
    }


def fetch_india_search_cards():
    cards = []

    source_priority = {
        "Indeed India": 500,
        "Naukri": 450,
        "LinkedIn": 400,
        "Cutshort": 350,
        "Wellfound": 300,
    }

    ai_locations = [
        "Remote India",
        "Noida",
        "Gurgaon",
        "Delhi NCR",
    ]

    bdm_locations = [
        "Remote India",
        "Noida",
        "Gurgaon",
        "Gurugram",
        "Delhi NCR",
    ]

    # Keep this intentionally limited so the UI does not explode.
    top_ai_queries = AI_SEARCH_QUERIES[:14]
    top_bdm_queries = BDM_SEARCH_QUERIES[:12]

    for query in top_ai_queries:
        for location in ai_locations:
            cards.append(
                create_search_card(
                    source="Indeed India",
                    role_type="AI",
                    query=query,
                    location=location,
                    url=build_indeed_url(
                        query,
                        location,
                    ),
                    source_priority=source_priority["Indeed India"],
                )
            )

            cards.append(
                create_search_card(
                    source="Naukri",
                    role_type="AI",
                    query=query,
                    location=location,
                    url=build_naukri_url(
                        query,
                        location,
                    ),
                    source_priority=source_priority["Naukri"],
                )
            )

            cards.append(
                create_search_card(
                    source="LinkedIn",
                    role_type="AI",
                    query=query,
                    location=location,
                    url=build_linkedin_url(
                        query,
                        location,
                    ),
                    source_priority=source_priority["LinkedIn"],
                )
            )

    for query in top_bdm_queries:
        for location in bdm_locations:
            cards.append(
                create_search_card(
                    source="Indeed India",
                    role_type="US IT Recruiter",
                    query=query,
                    location=location,
                    url=build_indeed_url(
                        query,
                        location,
                    ),
                    source_priority=source_priority["Indeed India"],
                )
            )

            cards.append(
                create_search_card(
                    source="Naukri",
                    role_type="US IT Recruiter",
                    query=query,
                    location=location,
                    url=build_naukri_url(
                        query,
                        location,
                    ),
                    source_priority=source_priority["Naukri"],
                )
            )

            cards.append(
                create_search_card(
                    source="LinkedIn",
                    role_type="US IT Recruiter",
                    query=query,
                    location=location,
                    url=build_linkedin_url(
                        query,
                        location,
                    ),
                    source_priority=source_priority["LinkedIn"],
                )
            )

    for query in AI_SEARCH_QUERIES[:10]:
        cards.append(
            create_search_card(
                source="Cutshort",
                role_type="AI",
                query=query,
                location="Remote India",
                url=build_cutshort_url(
                    query,
                ),
                source_priority=source_priority["Cutshort"],
            )
        )

        cards.append(
            create_search_card(
                source="Wellfound",
                role_type="AI",
                query=query,
                location="Remote India",
                url=build_wellfound_url(
                    query,
                ),
                source_priority=source_priority["Wellfound"],
            )
        )

    for query in BDM_SEARCH_QUERIES[:8]:
        cards.append(
            create_search_card(
                source="Cutshort",
                role_type="US IT Recruiter",
                query=query,
                location="Delhi NCR",
                url=build_cutshort_url(
                    query,
                ),
                source_priority=source_priority["Cutshort"],
            )
        )

    return cards


# =========================================================
# ARBEITNOW - LOW PRIORITY BACKUP
# =========================================================

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

    clean_description = strip_html(
        clean_description
    )

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

    # Arbeitnow is now backup only.
    # Reject unknown foreign remote listings early.
    if (
        remote
        and remote_eligibility
        not in [
            "India",
            "Worldwide",
        ]
    ):
        return None

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
            "Arbeitnow Backup",

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
            False,
    }


def fetch_arbeitnow_jobs(
    pages: int = 1,
):
    jobs = []

    pages = max(
        1,
        min(
            pages,
            2,
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
            normalized_job = normalize_arbeitnow_job(
                raw_job
            )

            if normalized_job is not None:
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


# =========================================================
# REMOTE OK - LOW PRIORITY BACKUP
# =========================================================

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

    role_type = classify_remoteok_job(
        title=title,
        description=clean_description,
        tags=tags,
    )

    if role_type is None:
        return None

    description_lower = clean_description.lower()

    obvious_not_remote = any(
        phrase in description_lower
        for phrase in [
            "there is no option to work remotely",
            "work must be completed at the physical location",
            "on-site only",
            "onsite only",
        ]
    )

    if obvious_not_remote:
        return None

    remote_eligibility = detect_remote_eligibility(
        title=title,
        location=location,
        description=clean_description,
    )

    if remote_eligibility not in [
        "India",
        "Worldwide",
    ]:
        return None

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

    if salary_min and salary_max:
        experience = (
            f"${salary_min:,} - "
            f"${salary_max:,}"
        )

    elif salary_min:
        experience = f"From ${salary_min:,}"

    elif salary_max:
        experience = f"Up to ${salary_max:,}"

    else:
        experience = "Not specified"

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
            "Remote OK Backup",

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
            False,
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

    for raw_job in payload[1:]:
        if not isinstance(
            raw_job,
            dict,
        ):
            continue

        normalized_job = normalize_remoteok_job(
            raw_job
        )

        if normalized_job is not None:
            jobs.append(
                normalized_job
            )

    return jobs


# =========================================================
# DEDUPE + AGGREGATION
# =========================================================

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
        title = normalize_dedupe_text(
            job.get("title")
        )

        company = normalize_dedupe_text(
            job.get("company")
        )

        url = normalize_dedupe_text(
            job.get("job_url")
        )

        if not title or not company:
            continue

        key = (
            title,
            company,
            url,
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

    # Priority source: India-focused search cards.
    # These are safe discovery cards for portals where
    # direct scraping/automation should not be the first step.
    try:
        all_jobs.extend(
            fetch_india_search_cards()
        )

    except Exception as error:
        source_errors.append(
            f"India Search Cards: {error}"
        )

    # Existing company/ATS sources remain useful because
    # Roleza can inspect and prepare external ATS applications.
    try:
        greenhouse_result = fetch_greenhouse_jobs()

        all_jobs.extend(
            greenhouse_result.get(
                "jobs",
                [],
            )
        )

        for error in greenhouse_result.get(
            "errors",
            [],
        ):
            source_errors.append(
                f"Greenhouse: {error}"
            )

    except Exception as error:
        source_errors.append(
            f"Greenhouse: {error}"
        )

    try:
        company_result = fetch_company_watchlist_jobs()

        all_jobs.extend(
            company_result.get(
                "jobs",
                [],
            )
        )

        for error in company_result.get(
            "errors",
            [],
        ):
            source_errors.append(
                f"Company Watchlist: {error}"
            )

    except Exception as error:
        source_errors.append(
            f"Company Watchlist: {error}"
        )

    # Low-priority backups only.
    try:
        all_jobs.extend(
            fetch_arbeitnow_jobs(
                pages=1
            )
        )

    except requests.RequestException as error:
        source_errors.append(
            f"Arbeitnow Backup: {error}"
        )

    except Exception as error:
        source_errors.append(
            f"Arbeitnow Backup: {error}"
        )

    try:
        all_jobs.extend(
            fetch_remoteok_jobs()
        )

    except requests.RequestException as error:
        source_errors.append(
            f"Remote OK Backup: {error}"
        )

    except Exception as error:
        source_errors.append(
            f"Remote OK Backup: {error}"
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
            "Indeed India",
            "Naukri",
            "LinkedIn",
            "Cutshort",
            "Wellfound",
            "Greenhouse",
            "Company Watchlist",
            "Arbeitnow Backup",
            "Remote OK Backup",
        ],
    }