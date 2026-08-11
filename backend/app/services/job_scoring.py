from datetime import datetime, timezone
import re


# =========================================================
# AI PROFILE
# =========================================================

AI_PROFILE_SKILLS = {
    "Python": [
        "python",
    ],
    "FastAPI": [
        "fastapi",
    ],
    "React": [
        "react",
        "reactjs",
        "react.js",
    ],
    "LLMs": [
        "llm",
        "large language model",
        "large language models",
    ],
    "Generative AI": [
        "generative ai",
        "genai",
        "gen ai",
    ],
    "RAG": [
        "rag",
        "retrieval augmented generation",
        "retrieval-augmented generation",
    ],
    "AI Agents": [
        "ai agent",
        "ai agents",
        "agentic ai",
        "agentic workflow",
        "agentic workflows",
        "agent orchestration",
        "ai orchestration",
    ],
    "Prompt Engineering": [
        "prompt engineering",
        "prompt design",
        "prompting",
        "prompt engineer",
        "prompt decomposition",
    ],
    "Anthropic / Claude": [
        "anthropic",
        "claude",
        "claude code",
    ],
    "OpenAI": [
        "openai",
        "gpt",
        "chatgpt",
    ],
    "APIs": [
        "api",
        "apis",
        "rest api",
        "restful api",
    ],
    "Automation": [
        "automation",
        "automations",
        "workflow automation",
        "ai automation",
    ],
    "Document AI": [
        "document analysis",
        "document processing",
        "pdf processing",
        "document intelligence",
    ],
    "NLP": [
        "nlp",
        "natural language processing",
    ],
    "AI Testing / Evaluation": [
        "ai testing",
        "ai evaluation",
        "evaluate ai",
        "model evaluation",
        "llm evaluation",
        "quality assurance",
        "qa testing",
    ],
    "AI Product Building": [
        "build features",
        "feature requirements",
        "ship features",
        "product requirements",
        "ai product",
        "ai-native",
        "ai native",
    ],
}


AI_STRONG_TITLE_KEYWORDS = [
    "claude code operator",
    "claude operator",
    "ai operator",
    "ai engineer",
    "artificial intelligence engineer",
    "generative ai engineer",
    "genai engineer",
    "ai developer",
    "ai automation engineer",
    "ai automation specialist",
    "ai automation generalist",
    "applied ai engineer",
    "ai associate",
    "ai specialist",
    "llm engineer",
    "llm application engineer",
    "agentic ai engineer",
    "ai agent engineer",
    "junior ai agent engineer",
    "prompt engineer",
    "prompt engineering specialist",
    "ai workflow engineer",
    "ai workflow specialist",
    "ai implementation specialist",
    "ai integration engineer",
    "ai solutions engineer",
    "ai technical specialist",
    "ai technical consultant",
    "ai product specialist",
    "ai testing engineer",
    "ai evaluation specialist",
    "ai native builder",
    "ai-native builder",
    "ai systems builder",
]


AI_RELEVANT_TITLE_KEYWORDS = [
    "machine learning engineer",
    "ml engineer",
    "nlp engineer",
    "data scientist",
    "forward deployed engineer",
    "ai researcher",
    "research engineer",
    "machine learning scientist",
    "automation engineer",
    "automation specialist",
    "workflow specialist",
    "technical consultant",
    "solutions engineer",
    "implementation specialist",
    "product specialist",
    "llm trainer",
    "ai trainer",
]


AI_FAST_APPLY_TITLE_BONUS = [
    "claude",
    "operator",
    "prompt",
    "agent",
    "agentic",
    "automation",
    "workflow",
    "llm",
    "ai testing",
    "ai evaluation",
    "ai native",
    "ai-native",
]


# =========================================================
# BDM PROFILE
# =========================================================

BDM_PROFILE_SKILLS = {
    "Business Development": [
        "business development",
        "bdm",
    ],
    "US IT": [
        "us it",
        "us staffing",
        "us recruitment",
        "us recruiter",
        "us technical recruiter",
    ],
    "Technical Recruiting": [
        "technical recruiter",
        "technical recruiting",
        "it recruiter",
        "it recruitment",
    ],
    "Talent Acquisition": [
        "talent acquisition",
        "ta specialist",
        "ta executive",
        "recruitment specialist",
        "recruitment executive",
    ],
    "Candidate Sourcing": [
        "candidate sourcing",
        "sourcing candidates",
        "talent sourcing",
        "sourcing specialist",
    ],
    "Staffing": [
        "staffing",
        "staffing industry",
        "us staffing",
    ],
    "Bench Sales": [
        "bench sales",
        "bench sales recruiter",
        "bench marketing",
    ],
    "Account Management": [
        "account management",
        "account manager",
        "client management",
    ],
    "Customer Success": [
        "customer success",
        "customer relationship",
        "customer relationships",
    ],
    "Client Acquisition": [
        "client acquisition",
        "new client",
        "new business",
    ],
    "Vendor Management": [
        "vendor management",
        "vendor relations",
    ],
    "Sales": [
        "sales",
        "sales pipeline",
        "lead generation",
    ],
}


BDM_STRONG_TITLE_KEYWORDS = [
    "business development manager",
    "business development executive",
    "business development associate",
    "business development representative",
    "business development specialist",
    "us it recruiter",
    "us recruiter",
    "technical recruiter",
    "it recruiter",
    "staffing recruiter",
    "us staffing recruiter",
    "resource development manager",
    "bench sales recruiter",
    "talent acquisition specialist",
    "talent acquisition executive",
    "talent acquisition lead",
    "recruitment manager",
    "recruitment specialist",
    "delivery manager staffing",
    "staffing business development",
    "recruitment business development",
]


# =========================================================
# SENIORITY
# =========================================================

HIGHLY_SENIOR_TITLE_WORDS = [
    "staff ",
    "principal",
    "director",
    "head of",
    "vice president",
    "vp ",
    "chief ",
    "architect",
]

SENIOR_TITLE_WORDS = [
    "senior",
    "sr.",
    "sr ",
    "lead ",
]

VERY_HIGH_EXPERIENCE = [
    "10+ years",
    "10 years",
    "11+ years",
    "11 years",
    "12+ years",
    "12 years",
    "15+ years",
    "15 years",
]

HIGH_EXPERIENCE = [
    "8+ years",
    "8 years",
    "9+ years",
    "9 years",
]

MID_HIGH_EXPERIENCE = [
    "6+ years",
    "6 years",
    "7+ years",
    "7 years",
]

MODERATE_EXPERIENCE = [
    "5+ years",
    "5 years",
]

GOOD_ENTRY_EXPERIENCE = [
    "0-1 years",
    "0–1 years",
    "0-2 years",
    "0–2 years",
    "1-2 years",
    "1–2 years",
    "1+ years",
    "2+ years",
    "2 years",
    "3+ years",
    "3 years",
    "fresher",
    "freshers",
    "entry level",
    "entry-level",
    "junior",
]

JUNIOR_TITLE_WORDS = [
    "junior",
    "associate",
    "entry level",
    "entry-level",
    "graduate",
    "intern",
    "trainee",
]


# =========================================================
# HELPERS
# =========================================================

def normalize(value):
    return re.sub(
        r"\s+",
        " ",
        (value or "").lower(),
    ).strip()


def calculate_job_age_days(created_at):
    if not created_at:
        return None

    try:
        posted = datetime.fromtimestamp(
            int(created_at),
            tz=timezone.utc,
        )

        now = datetime.now(
            timezone.utc
        )

        return max(
            0,
            int(
                (
                    now
                    - posted
                ).total_seconds()
                // 86400
            ),
        )

    except Exception:
        return None


def freshness_label(age_days):
    if age_days is None:
        return "Unknown"

    if age_days == 0:
        return "Today"

    if age_days == 1:
        return "1 day old"

    return f"{age_days} days old"


def find_profile_matches(
    text,
    profile_skills,
):
    matched = []

    for display_name, keywords in profile_skills.items():
        if any(
            keyword in text
            for keyword in keywords
        ):
            matched.append(
                display_name
            )

    return matched


def contains_any(
    text,
    phrases,
):
    return any(
        phrase in text
        for phrase in phrases
    )


def add_reason(
    reasons,
    message,
):
    if message and message not in reasons:
        reasons.append(
            message
        )


def is_search_card(job):
    return bool(
        job.get("is_search_card")
    )


# =========================================================
# AI FIT
# =========================================================

def calculate_ai_fit(job):
    title = normalize(
        job.get("title")
    )

    description = normalize(
        job.get("full_description")
        or job.get("description")
    )

    source = normalize(
        job.get("source")
    )

    combined = f"{title} {description}"

    score = 0
    reasons = []

    matched_skills = find_profile_matches(
        combined,
        AI_PROFILE_SKILLS,
    )

    if is_search_card(job):
        score += 42

        add_reason(
            reasons,
            "High-priority AI search source",
        )

        if source in [
            "indeed india",
            "naukri",
            "linkedin",
        ]:
            score += 14

            add_reason(
                reasons,
                "Priority India job portal",
            )

    if contains_any(
        title,
        AI_STRONG_TITLE_KEYWORDS,
    ):
        score += 38

        add_reason(
            reasons,
            "Strong match to target AI role",
        )

    elif contains_any(
        title,
        AI_RELEVANT_TITLE_KEYWORDS,
    ):
        score += 26

        add_reason(
            reasons,
            "Relevant AI/automation role",
        )

    else:
        score += 10

        add_reason(
            reasons,
            "Partial AI role match",
        )

    if contains_any(
        title,
        AI_FAST_APPLY_TITLE_BONUS,
    ):
        score += 10

        add_reason(
            reasons,
            "Matches fast-apply AI role family",
        )

    skill_score = min(
        len(matched_skills) * 6,
        42,
    )

    score += skill_score

    if matched_skills:
        preview = ", ".join(
            matched_skills[:6]
        )

        add_reason(
            reasons,
            f"Matched skills: {preview}",
        )

    if len(matched_skills) >= 6:
        score += 6

        add_reason(
            reasons,
            "Strong technical overlap",
        )

    elif len(matched_skills) >= 3:
        score += 3

        add_reason(
            reasons,
            "Good technical overlap",
        )

    elif len(matched_skills) <= 1 and not is_search_card(job):
        score -= 8

        add_reason(
            reasons,
            "Limited technical overlap",
        )

    if contains_any(
        title,
        JUNIOR_TITLE_WORDS,
    ):
        score += 12

        add_reason(
            reasons,
            "Career-level friendly",
        )

    if contains_any(
        description,
        GOOD_ENTRY_EXPERIENCE,
    ):
        score += 8

        add_reason(
            reasons,
            "Accessible experience requirement",
        )

    if contains_any(
        title,
        HIGHLY_SENIOR_TITLE_WORDS,
    ):
        score -= 28

        add_reason(
            reasons,
            "Highly senior role",
        )

    elif contains_any(
        title,
        SENIOR_TITLE_WORDS,
    ):
        score -= 10

        add_reason(
            reasons,
            "Senior role",
        )

    if contains_any(
        description,
        VERY_HIGH_EXPERIENCE,
    ):
        score -= 35

        add_reason(
            reasons,
            "Requires 10+ years experience",
        )

    elif contains_any(
        description,
        HIGH_EXPERIENCE,
    ):
        score -= 27

        add_reason(
            reasons,
            "Requires 8+ years experience",
        )

    elif contains_any(
        description,
        MID_HIGH_EXPERIENCE,
    ):
        score -= 20

        add_reason(
            reasons,
            "Requires 6-7 years experience",
        )

    elif contains_any(
        description,
        MODERATE_EXPERIENCE,
    ):
        score -= 8

        add_reason(
            reasons,
            "Requires around 5 years experience",
        )

    return (
        score,
        reasons,
        matched_skills,
    )


# =========================================================
# BDM FIT
# =========================================================

def calculate_bdm_fit(job):
    title = normalize(
        job.get("title")
    )

    description = normalize(
        job.get("full_description")
        or job.get("description")
    )

    source = normalize(
        job.get("source")
    )

    combined = f"{title} {description}"

    score = 0
    reasons = []

    matched_skills = find_profile_matches(
        combined,
        BDM_PROFILE_SKILLS,
    )

    if is_search_card(job):
        score += 40

        add_reason(
            reasons,
            "High-priority BDM/recruiting search source",
        )

        if source in [
            "indeed india",
            "naukri",
            "linkedin",
        ]:
            score += 14

            add_reason(
                reasons,
                "Priority India job portal",
            )

    if contains_any(
        title,
        BDM_STRONG_TITLE_KEYWORDS,
    ):
        score += 38

        add_reason(
            reasons,
            "Strong BDM/recruiting role match",
        )

    elif (
        "business development" in title
        or "recruiter" in title
        or "recruitment" in title
        or "talent acquisition" in title
        or "staffing" in title
        or "account manager" in title
        or "bench sales" in title
    ):
        score += 28

        add_reason(
            reasons,
            "Relevant BDM/recruiting role",
        )

    else:
        score += 12

        add_reason(
            reasons,
            "Partial BDM role match",
        )

    skill_score = min(
        len(matched_skills) * 5,
        35,
    )

    score += skill_score

    if matched_skills:
        preview = ", ".join(
            matched_skills[:6]
        )

        add_reason(
            reasons,
            f"Matched experience: {preview}",
        )

    if len(matched_skills) >= 5:
        add_reason(
            reasons,
            "Strong BDM experience overlap",
        )

    elif len(matched_skills) >= 3:
        add_reason(
            reasons,
            "Good BDM experience overlap",
        )

    if contains_any(
        title,
        JUNIOR_TITLE_WORDS,
    ):
        score += 5

        add_reason(
            reasons,
            "Career-level friendly",
        )

    if contains_any(
        title,
        HIGHLY_SENIOR_TITLE_WORDS,
    ):
        score -= 25

        add_reason(
            reasons,
            "Highly senior role",
        )

    elif contains_any(
        title,
        SENIOR_TITLE_WORDS,
    ):
        score -= 8

        add_reason(
            reasons,
            "Senior role",
        )

    if contains_any(
        description,
        VERY_HIGH_EXPERIENCE,
    ):
        score -= 25

        add_reason(
            reasons,
            "Requires 10+ years experience",
        )

    elif contains_any(
        description,
        HIGH_EXPERIENCE,
    ):
        score -= 18

        add_reason(
            reasons,
            "Requires 8+ years experience",
        )

    elif contains_any(
        description,
        MID_HIGH_EXPERIENCE,
    ):
        score -= 10

        add_reason(
            reasons,
            "Requires 6-7 years experience",
        )

    return (
        score,
        reasons,
        matched_skills,
    )


# =========================================================
# LOCATION FIT
# =========================================================

def apply_location_score(
    score,
    reasons,
    job,
):
    eligibility = normalize(
        job.get("remote_eligibility")
        or "unknown"
    )

    location = normalize(
        job.get("location")
    )

    source = normalize(
        job.get("source")
    )

    if eligibility == "india":
        score += 24

        add_reason(
            reasons,
            "Eligible from India",
        )

    elif eligibility == "worldwide":
        score += 20

        add_reason(
            reasons,
            "Worldwide remote",
        )

    elif (
        "remote india" in location
        or (
            "india" in location
            and "remote" in location
        )
    ):
        score += 24

        add_reason(
            reasons,
            "Remote role in India",
        )

    elif any(
        place in location
        for place in [
            "noida",
            "gurgaon",
            "gurugram",
            "delhi",
            "delhi ncr",
            "ncr",
        ]
    ):
        score += 22

        add_reason(
            reasons,
            "Target NCR location",
        )

    elif "india" in location:
        score += 14

        add_reason(
            reasons,
            "India-based role",
        )

    elif (
        eligibility == "unknown"
        and "remote" in location
        and source in [
            "indeed india",
            "naukri",
            "linkedin",
            "cutshort",
            "wellfound",
        ]
    ):
        score += 6

        add_reason(
            reasons,
            "India portal remote role needs verification",
        )

    elif (
        eligibility == "unknown"
        and "remote" in location
    ):
        score += 2

        add_reason(
            reasons,
            "Remote eligibility needs verification",
        )

    if eligibility == "us only":
        score -= 60

        add_reason(
            reasons,
            "US-only eligibility",
        )

    elif eligibility == "eu/uk only":
        score -= 60

        add_reason(
            reasons,
            "EU/UK-only eligibility",
        )

    elif eligibility == "emea":
        score -= 45

        add_reason(
            reasons,
            "EMEA-restricted role",
        )

    elif eligibility == "relocation / onsite":
        score -= 50

        add_reason(
            reasons,
            "Relocation or onsite restriction",
        )

    return score, reasons


# =========================================================
# APPLICATION RESTRICTIONS
# =========================================================

def apply_application_restrictions(
    score,
    reasons,
    job,
):
    title = normalize(
        job.get("title")
    )

    description = normalize(
        job.get("full_description")
        or job.get("description")
    )

    combined = f"{title} {description}"

    clearance_phrases = [
        "top secret clearance",
        "ts clearance",
        "security clearance required",
        "active clearance",
        "active security clearance",
        "must hold a security clearance",
        "secret clearance required",
    ]

    if contains_any(
        combined,
        clearance_phrases,
    ):
        score -= 60

        add_reason(
            reasons,
            "Security clearance required",
        )

    citizenship_phrases = [
        "us citizenship required",
        "u.s. citizenship required",
        "must be a us citizen",
        "must be a u.s. citizen",
        "us citizen required",
        "u.s. citizen required",
        "green card required",
        "greencard required",
        "us citizen or green card",
        "us citizen or greencard",
    ]

    if contains_any(
        combined,
        citizenship_phrases,
    ):
        score -= 50

        add_reason(
            reasons,
            "US citizenship/work authorization restriction",
        )

    sponsorship_phrases = [
        "no visa sponsorship",
        "unable to sponsor",
        "cannot sponsor",
        "will not sponsor",
        "must be authorized to work in the united states",
        "must be authorised to work in the united states",
        "us work authorization required",
    ]

    if contains_any(
        combined,
        sponsorship_phrases,
    ):
        score -= 35

        add_reason(
            reasons,
            "Work authorization restriction",
        )

    foreign_onsite_phrases = [
        "relocation required",
        "must relocate",
        "relocate to",
        "onsite only",
        "on-site only",
        "work from office",
        "office based",
        "office-based",
    ]

    if contains_any(
        combined,
        foreign_onsite_phrases,
    ):
        score -= 35

        add_reason(
            reasons,
            "Relocation/onsite language detected",
        )

    return score, reasons


# =========================================================
# FRESHNESS
# =========================================================

def apply_freshness_score(
    score,
    reasons,
    job,
):
    age_days = calculate_job_age_days(
        job.get("created_at")
    )

    if age_days is None:
        add_reason(
            reasons,
            "Posting date unavailable",
        )

        return (
            score,
            reasons,
            age_days,
        )

    if age_days == 0:
        score += 12

        add_reason(
            reasons,
            "Posted today",
        )

    elif age_days <= 2:
        score += 9

        add_reason(
            reasons,
            "Very fresh posting",
        )

    elif age_days <= 7:
        score += 5

        add_reason(
            reasons,
            "Fresh posting",
        )

    elif age_days <= 14:
        score += 1

    elif age_days <= 30:
        score -= 10

        add_reason(
            reasons,
            "Posting is over 2 weeks old",
        )

    else:
        score -= 22

        add_reason(
            reasons,
            "Older posting",
        )

    return (
        score,
        reasons,
        age_days,
    )


# =========================================================
# FINAL SCORING
# =========================================================

def score_job(job):
    role_type = job.get(
        "role_type"
    )

    if role_type == "AI":
        (
            score,
            reasons,
            matched_skills,
        ) = calculate_ai_fit(
            job
        )

    else:
        (
            score,
            reasons,
            matched_skills,
        ) = calculate_bdm_fit(
            job
        )

    before_location = score

    score, reasons = apply_location_score(
        score,
        reasons,
        job,
    )

    location_points = (
        score
        - before_location
    )

    before_restrictions = score

    score, reasons = apply_application_restrictions(
        score,
        reasons,
        job,
    )

    restriction_points = (
        score
        - before_restrictions
    )

    before_freshness = score

    (
        score,
        reasons,
        age_days,
    ) = apply_freshness_score(
        score,
        reasons,
        job,
    )

    freshness_points = (
        score
        - before_freshness
    )

    raw_score = score

    score = max(
        0,
        min(
            100,
            round(score),
        ),
    )

    if score >= 80:
        priority = "High"

    elif score >= 60:
        priority = "Medium"

    else:
        priority = "Low"

    eligibility = normalize(
        job.get(
            "remote_eligibility"
        )
    )

    safe_location = (
        eligibility
        in [
            "india",
            "worldwide",
        ]
    )

    restricted = (
        restriction_points < 0
        or eligibility
        in [
            "us only",
            "eu/uk only",
            "emea",
            "relocation / onsite",
        ]
    )

    search_card = is_search_card(job)

    if (
        score >= 80
        and safe_location
        and not restricted
        and not search_card
    ):
        application_recommendation = (
            "Strong candidate for auto-apply"
        )

    elif (
        score >= 70
        and search_card
        and not restricted
    ):
        application_recommendation = (
            "Open job board and apply to matching listings"
        )

    elif (
        score >= 60
        and not restricted
    ):
        application_recommendation = (
            "Review before applying"
        )

    else:
        application_recommendation = (
            "Do not auto-apply"
        )

    job["fit_score"] = score

    job["priority"] = priority

    job["fit_reasons"] = reasons[:8]

    job["matched_skills"] = matched_skills

    job["age_days"] = age_days

    job["freshness"] = freshness_label(
        age_days
    )

    job["application_recommendation"] = (
        application_recommendation
    )

    job["fit_breakdown"] = {
        "raw_score":
            raw_score,

        "location_adjustment":
            location_points,

        "restriction_adjustment":
            restriction_points,

        "freshness_adjustment":
            freshness_points,
    }

    return job