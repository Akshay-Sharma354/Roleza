from pathlib import Path
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from playwright.async_api import (
    async_playwright,
    Page,
)

from app.services.profile import (
    load_application_profile,
)


router = APIRouter(
    prefix="/browser",
    tags=["Browser Automation"],
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

RESUME_DIR = BASE_DIR / "resumes"


RESUME_FILES = {
    "AI": (
        RESUME_DIR
        / "Akshay-Sharma_AI.pdf"
    ),
    "US IT Recruiter": (
        RESUME_DIR
        / "Akshay-Sharma_BDM.docx"
    ),
}


SAFE_FIELD_KEYWORDS = [
    "first name",
    "firstname",
    "given name",
    "preferred first name",
    "last name",
    "lastname",
    "surname",
    "family name",
    "full name",
    "_systemfield_name",
    "type here... name",
    "email",
    "phone",
    "telephone",
    "mobile",
    "resume",
    "cv",
    "curriculum vitae",
    "country off country",
    "country in which you are located",
    "current country of residence",
    "country of residence",
]


DRAFTABLE_QUESTION_KEYWORDS = [
    "why are you interested",
    "why do you want",
    "what interests you",
    "what excites you",
    "describe your experience",
    "describe your most",
    "describe a project",
    "describe a time",
    "tell us about",
    "tell me about",
    "customer-facing project",
    "customer facing project",
    "ai workflows",
    "ai-powered solutions",
    "ai powered solutions",
    "implemented ai",
    "production ai",
    "programming languages",
    "multiple programming languages",
    "technical experience",
    "relevant experience",
    "experience working with",
    "experience building",
    "experience implementing",
    "experience developing",
    "experience deploying",
    "complex project",
    "challenging project",
    "professional experience",
    "customer-facing technical role",
    "customer facing technical role",
]


USER_DECISION_KEYWORDS = [
    "work authorization",
    "work eligibility",
    "eligible to work",
    "authorized to work",
    "authorised to work",
    "legally eligible",
    "legally authorized",
    "legally authorised",
    "visa sponsorship",
    "sponsorship",
    "require sponsorship",
    "status that allows you to work",
    "work and live in that country",

    # Location / residency eligibility
    "do you currently live in this location",
    "currently live in this location",
    "open to candidates in",
    "currently reside in",
    "currently living in",

    # Experience / self-rating questions
    "years of professional software engineering experience",
    "years of software engineering experience",
    "do you have over",
    "rate yourself",
    "scale from 0 to 5",
    "scale from 1 to 5",

    # Employment history / restrictions
    "employment agreements",
    "post-employment restrictions",
    "post employment restrictions",
    "previously worked at",
    "previously worked for",
    "previously consulted for",
    "worked at or consulted for",

    # Required external profile fields
    "linkedin profile",

    "salary expectation",
    "salary expectations",
    "expected salary",
    "desired salary",
    "compensation expectation",
    "current salary",
    "notice period",
    "security clearance",
    "citizenship",
    "willing to relocate",
    "relocation",
    "willing to travel",
    "able to travel",
    "travel approximately",
    "travel requirement",
    "non-compete",
    "non compete",
    "how did you hear about",
    "hired through remote as a third party",
    "third party",
    "assessment",
    "take-home",
    "take home",
    "privacy notice",
]


CONSENT_KEYWORDS = [
    "consent",
    "recording",
    "record interview",
    "recorded interview",
    "auto-transcript",
    "auto transcript",
    "transcription",
    "brighthire",
    "privacy consent",
    "gdpr",
    "notice at collection",
]


PERSONAL_QUESTION_KEYWORDS = [
    "race",
    "ethnicity",
    "gender",
    "sexual orientation",
    "lgbt",
    "lgbtq",
    "lgbtqia",
    "disability",
    "disabled",
    "veteran",
    "demographic",
    "self-identification",
    "self identification",
    "pronouns",
]


CAPTCHA_KEYWORDS = [
    "captcha",
    "recaptcha",
    "hcaptcha",
    "verify you are human",
    "human verification",
    "cloudflare challenge",
]


LOGIN_KEYWORDS = [
    "sign in",
    "log in",
    "login",
    "create account",
    "create an account",
]


DEAD_JOB_KEYWORDS = [
    "job not found",
    "the job you requested was not found",
    "this job is no longer available",
    "this position is no longer available",
    "position is no longer available",
    "position has been filled",
    "this role has been filled",
    "applications are closed",
    "applications have closed",
    "this job has expired",
    "job has expired",
    "job expired",
    "posting has expired",
    "no longer accepting applications",
    "we are no longer accepting applications",
    "this position has been closed",
    "this job has been closed",
    "404 not found",
    "page not found",
]


APPLY_BUTTON_TEXT = [
    "apply now",
    "apply for this job",
    "apply",
]


class InspectApplicationRequest(
    BaseModel
):
    job_url: str


class StartApplicationRequest(
    BaseModel
):
    job_url: str

    role_type: str = "AI"

    first_name: str = ""
    last_name: str = ""
    full_name: str = ""

    email: str = ""
    phone: str = ""
    country: str = ""


def normalize(value):
    return re.sub(
        r"\s+",
        " ",
        (
            value
            or ""
        ).lower(),
    ).strip()


def contains_any(
    text,
    keywords,
):
    return any(
        keyword in text
        for keyword in keywords
    )


def validate_url(job_url):
    return job_url.startswith(
        (
            "http://",
            "https://",
        )
    )


def get_resume_path(
    role_type,
):
    resume_path = (
        RESUME_FILES.get(
            role_type
        )
    )

    if resume_path is None:
        return None

    if not resume_path.exists():
        return None

    return resume_path


def apply_saved_profile(
    request: StartApplicationRequest,
):
    profile = (
        load_application_profile()
    )

    if not request.first_name:
        request.first_name = profile.get(
            "first_name",
            "",
        )

    if not request.last_name:
        request.last_name = profile.get(
            "last_name",
            "",
        )

    if not request.full_name:
        request.full_name = profile.get(
            "full_name",
            "",
        )

    if not request.email:
        request.email = profile.get(
            "email",
            "",
        )

    if not request.phone:
        request.phone = profile.get(
            "phone",
            "",
        )

    if not request.country:
        request.country = profile.get(
            "country",
            "India",
        )

    return request


async def get_page_text(
    page: Page,
):
    try:
        return normalize(
            await page.locator(
                "body"
            ).inner_text()
        )

    except Exception:
        return ""


async def page_has_text(
    page: Page,
    keywords,
):
    body_text = (
        await get_page_text(
            page
        )
    )

    return contains_any(
        body_text,
        keywords,
    )


async def detect_dead_job(
    page: Page,
):
    body_text = (
        await get_page_text(
            page
        )
    )

    for phrase in DEAD_JOB_KEYWORDS:
        if phrase in body_text:
            return {
                "dead": True,
                "reason": phrase,
            }

    try:
        title = normalize(
            await page.title()
        )

    except Exception:
        title = ""

    for phrase in [
        "job not found",
        "page not found",
        "404",
    ]:
        if phrase in title:
            return {
                "dead": True,
                "reason": title,
            }

    return {
        "dead": False,
        "reason": None,
    }


async def detect_captcha(
    page: Page,
):
    selectors = [
        "iframe[src*='recaptcha']",
        "iframe[src*='hcaptcha']",
        "[class*='captcha']",
        "[id*='captcha']",
        "[data-sitekey]",
    ]

    for selector in selectors:
        try:
            if (
                await page.locator(
                    selector
                ).count()
                > 0
            ):
                return True

        except Exception:
            pass

    return await page_has_text(
        page,
        CAPTCHA_KEYWORDS,
    )


async def detect_login_wall(
    page: Page,
):
    try:
        if (
            await page.locator(
                'input[type="password"]'
            ).count()
            > 0
        ):
            return True

    except Exception:
        pass

    return await page_has_text(
        page,
        LOGIN_KEYWORDS,
    )


# =========================================================
# IMPORTANT:
# Click Apply AND follow new browser tabs/popups
# =========================================================

async def click_apply_and_follow(
    page: Page,
):
    """
    Find the real application destination.

    Priority:
    1. Read the Apply link href directly.
    2. Open that URL ourselves.
    3. Fall back to clicking buttons/links.
    4. Detect popup/new-tab navigation.
    """

    context = page.context

    # -----------------------------------------------------
    # FIRST: inspect Apply links and use their href directly
    # -----------------------------------------------------

    for text in APPLY_BUTTON_TEXT:
        pattern = re.compile(
            rf"^{re.escape(text)}$",
            re.IGNORECASE,
        )

        try:
            links = page.get_by_role(
                "link",
                name=pattern,
            )

            count = await links.count()

            for index in range(count):
                link = links.nth(index)

                href = (
                    await link.get_attribute(
                        "href"
                    )
                    or ""
                ).strip()

                if not href:
                    continue

                if href.startswith(
                    (
                        "#",
                        "javascript:",
                        "mailto:",
                        "tel:",
                    )
                ):
                    continue

                # Resolve relative URL in browser.
                absolute_url = await link.evaluate(
                    """
                    (el) => el.href
                    """
                )

                if (
                    absolute_url
                    and absolute_url
                    != page.url
                ):
                    application_page = (
                        await context.new_page()
                    )

                    await application_page.goto(
                        absolute_url,
                        wait_until="domcontentloaded",
                        timeout=45000,
                    )

                    await application_page.wait_for_timeout(
                        1500
                    )

                    return {
                        "opened": True,
                        "page": application_page,
                        "new_tab": True,
                        "method": "direct_href",
                        "application_url":
                            application_page.url,
                    }

        except Exception:
            pass

    # -----------------------------------------------------
    # SECOND: fall back to clicking Apply
    # -----------------------------------------------------

    for text in APPLY_BUTTON_TEXT:
        pattern = re.compile(
            rf"^{re.escape(text)}$",
            re.IGNORECASE,
        )

        candidates = []

        try:
            button = page.get_by_role(
                "button",
                name=pattern,
            )

            if (
                await button.count()
                > 0
            ):
                candidates.append(
                    button.first
                )

        except Exception:
            pass

        try:
            link = page.get_by_role(
                "link",
                name=pattern,
            )

            if (
                await link.count()
                > 0
            ):
                candidates.append(
                    link.first
                )

        except Exception:
            pass

        for candidate in candidates:
            try:
                pages_before = list(
                    context.pages
                )

                old_url = page.url

                await candidate.click()

                # Some job boards delay opening the ATS.
                await page.wait_for_timeout(
                    5000
                )

                pages_after = list(
                    context.pages
                )

                new_pages = [
                    current_page
                    for current_page in pages_after
                    if current_page
                    not in pages_before
                ]

                if new_pages:
                    application_page = (
                        new_pages[-1]
                    )

                    try:
                        await application_page.wait_for_load_state(
                            "domcontentloaded",
                            timeout=20000,
                        )
                    except Exception:
                        pass

                    await application_page.wait_for_timeout(
                        1500
                    )

                    return {
                        "opened": True,
                        "page":
                            application_page,
                        "new_tab": True,
                        "method":
                            "popup",
                        "application_url":
                            application_page.url,
                    }

                # Same-tab redirect.
                if page.url != old_url:
                    try:
                        await page.wait_for_load_state(
                            "domcontentloaded",
                            timeout=15000,
                        )
                    except Exception:
                        pass

                    return {
                        "opened": True,
                        "page": page,
                        "new_tab": False,
                        "method":
                            "same_tab_redirect",
                        "application_url":
                            page.url,
                    }

            except Exception:
                continue

    return {
        "opened": False,
        "page": page,
        "new_tab": False,
        "method": "not_found",
        "application_url": page.url,
    }


async def get_field_context(
    element,
):
    parts = []

    for attribute in [
        "name",
        "id",
        "placeholder",
        "aria-label",
        "autocomplete",
    ]:
        try:
            value = (
                await element.get_attribute(
                    attribute
                )
            )

            if value:
                parts.append(
                    value
                )

        except Exception:
            pass

    try:
        element_id = (
            await element.get_attribute(
                "id"
            )
        )

        if element_id:
            label = (
                element.page.locator(
                    f'label[for="{element_id}"]'
                )
            )

            if (
                await label.count()
                > 0
            ):
                parts.append(
                    await label.first.inner_text()
                )

    except Exception:
        pass

    return normalize(
        " ".join(parts)
    )


async def field_is_required(
    element,
    context,
):
    try:
        required = (
            await element.get_attribute(
                "required"
            )
        )

        if required is not None:
            return True

    except Exception:
        pass

    try:
        aria_required = normalize(
            await element.get_attribute(
                "aria-required"
            )
        )

        if aria_required == "true":
            return True

    except Exception:
        pass

    return (
        "*" in context
        or "required" in context
    )


def classify_field_context(
    context,
    required,
):
    if contains_any(
        context,
        PERSONAL_QUESTION_KEYWORDS,
    ):
        return (
            "personal_required"
            if required
            else "personal_optional"
        )

    if contains_any(
        context,
        USER_DECISION_KEYWORDS,
    ):
        return "user_decision"

    if contains_any(
        context,
        CONSENT_KEYWORDS,
    ):
        return "user_decision"

    if contains_any(
        context,
        DRAFTABLE_QUESTION_KEYWORDS,
    ):
        return "draftable"

    if contains_any(
        context,
        SAFE_FIELD_KEYWORDS,
    ):
        return "safe"

    if required:
        return "unknown_required"

    return "unknown_optional"


async def inspect_fields(
    page: Page,
):
    results = []

    elements = page.locator(
        "input, textarea, select"
    )

    count = (
        await elements.count()
    )

    for index in range(
        min(
            count,
            150,
        )
    ):
        element = (
            elements.nth(index)
        )

        try:
            tag_name = (
                await element.evaluate(
                    "(el) => "
                    "el.tagName.toLowerCase()"
                )
            )

            field_type = (
                await element.get_attribute(
                    "type"
                )
                or tag_name
            )

            context = (
                await get_field_context(
                    element
                )
            )

            if not context:
                continue

            required = (
                await field_is_required(
                    element,
                    context,
                )
            )

            category = (
                classify_field_context(
                    context,
                    required,
                )
            )

            results.append(
                {
                    "index": index,
                    "type": field_type,
                    "context":
                        context[:450],
                    "required":
                        required,
                    "category":
                        category,
                }
            )

        except Exception:
            continue

    return results


def build_field_summary(
    fields,
    captcha,
    login_wall,
):
    safe_fields = []
    draftable_questions = []
    user_decisions = []
    personal_questions = []
    unknown_required = []
    unknown_optional = []

    for field in fields:
        category = field.get(
            "category"
        )

        if category == "safe":
            safe_fields.append(field)

        elif category == "draftable":
            draftable_questions.append(
                field
            )

        elif category == "user_decision":
            user_decisions.append(
                field
            )

        elif category in [
            "personal_required",
            "personal_optional",
        ]:
            personal_questions.append(
                field
            )

        elif category == "unknown_required":
            unknown_required.append(
                field
            )

        elif category == "unknown_optional":
            unknown_optional.append(
                field
            )

    hard_blockers = []

    if captcha:
        hard_blockers.append(
            "CAPTCHA / human verification"
        )

    if login_wall:
        hard_blockers.append(
            "Login or account creation"
        )

    return {
        "hard_blockers":
            hard_blockers,

        "safe_fields":
            safe_fields,

        "draftable_questions":
            draftable_questions,

        "user_decisions":
            user_decisions,

        "personal_questions":
            personal_questions,

        "unknown_required_fields":
            unknown_required,

        "unknown_optional_fields":
            unknown_optional,

        "counts": {
            "total":
                len(fields),

            "safe":
                len(safe_fields),

            "draftable":
                len(
                    draftable_questions
                ),

            "user_decisions":
                len(
                    user_decisions
                ),

            "personal_questions":
                len(
                    personal_questions
                ),

            "unknown_required":
                len(
                    unknown_required
                ),

            "unknown_optional":
                len(
                    unknown_optional
                ),

            "hard_blockers":
                len(
                    hard_blockers
                ),
        },

        "can_prepare_application":
            not captcha
            and not login_wall,

        "can_submit_automatically":
            (
                not hard_blockers
                and not user_decisions
                and not personal_questions
                and not draftable_questions
                and not unknown_required
            ),
    }


async def safe_fill(
    page: Page,
    request: StartApplicationRequest,
):
    """
    Fill only safe, factual application fields.

    Strategy:
    1. Try common application labels directly.
    2. Handle country dropdowns.
    3. Fall back to Roleza's generic field classifier.
    """

    filled = []
    skipped = []

    async def fill_by_label(
        labels,
        value,
        field_name,
    ):
        if not value:
            return False

        for label in labels:
            try:
                locator = page.get_by_label(
                    re.compile(
                        label,
                        re.IGNORECASE,
                    )
                )

                count = await locator.count()

                for i in range(count):
                    element = locator.nth(i)

                    try:
                        if not await element.is_visible():
                            continue
                    except Exception:
                        pass

                    try:
                        await element.fill(
                            str(value)
                        )

                        filled.append(
                            field_name
                        )

                        return True

                    except Exception:
                        continue

            except Exception:
                continue

        return False

    # -------------------------------------------------
    # Direct safe profile fields
    # -------------------------------------------------

    await fill_by_label(
        [
            r"^first name",
            r"^given name",
        ],
        request.first_name,
        "First name",
    )

    await fill_by_label(
        [
            r"^preferred first name",
            r"^preferred name",
        ],
        request.first_name,
        "Preferred first name",
    )

    await fill_by_label(
        [
            r"^last name",
            r"^surname",
            r"^family name",
        ],
        request.last_name,
        "Last name",
    )

    await fill_by_label(
        [
            r"^full name",
        ],
        (
            request.full_name
            or (
                f"{request.first_name} "
                f"{request.last_name}"
            ).strip()
        ),
        "Full name",
    )

    await fill_by_label(
        [
            r"^email",
            r"email address",
        ],
        request.email,
        "Email",
    )

    await fill_by_label(
        [
            r"^phone",
            r"telephone",
            r"mobile",
        ],
        request.phone,
        "Phone",
    )

    # -------------------------------------------------
    # Country / country of residence
    # -------------------------------------------------

    if request.country:
        country_patterns = [
            r"^country$",
            r"country of residence",
            r"current country of residence",
            r"country in which you are located",
        ]

        country_done = False

        for pattern in country_patterns:
            try:
                locator = page.get_by_label(
                    re.compile(
                        pattern,
                        re.IGNORECASE,
                    )
                )

                count = await locator.count()

                for i in range(count):
                    element = locator.nth(i)

                    try:
                        tag_name = await element.evaluate(
                            "(el) => el.tagName.toLowerCase()"
                        )
                    except Exception:
                        tag_name = ""

                    if tag_name == "select":
                        try:
                            await element.select_option(
                                label=request.country
                            )

                            filled.append(
                                "Country"
                            )

                            country_done = True
                            break

                        except Exception:
                            try:
                                await element.select_option(
                                    value=request.country
                                )

                                filled.append(
                                    "Country"
                                )

                                country_done = True
                                break

                            except Exception:
                                pass

                    # Custom combobox / React dropdown.
                    try:
                        await element.click()

                        option = page.get_by_role(
                            "option",
                            name=re.compile(
                                rf"^{re.escape(request.country)}$",
                                re.IGNORECASE,
                            ),
                        )

                        if await option.count():
                            await option.first.click()

                            filled.append(
                                "Country"
                            )

                            country_done = True
                            break

                    except Exception:
                        pass

                    try:
                        await element.fill(
                            request.country
                        )

                        await page.wait_for_timeout(
                            300
                        )

                        option = page.get_by_text(
                            re.compile(
                                rf"^{re.escape(request.country)}$",
                                re.IGNORECASE,
                            )
                        )

                        if await option.count():
                            await option.first.click()

                        filled.append(
                            "Country"
                        )

                        country_done = True
                        break

                    except Exception:
                        pass

                if country_done:
                    break

            except Exception:
                continue

        # Some ATS dropdowns do not expose a normal label.
        if not country_done:
            try:
                country_text = page.get_by_text(
                    re.compile(
                        r"^country$",
                        re.IGNORECASE,
                    )
                )

                if await country_text.count():
                    await country_text.first.click()

                    await page.wait_for_timeout(
                        300
                    )

                    india_option = page.get_by_text(
                        re.compile(
                            rf"^{re.escape(request.country)}$",
                            re.IGNORECASE,
                        )
                    )

                    if await india_option.count():
                        await india_option.last.click()

                        filled.append(
                            "Country"
                        )

                        country_done = True

            except Exception:
                pass

        if not country_done:
            skipped.append(
                "Country"
            )

    # -------------------------------------------------
    # Generic safe-field fallback
    # -------------------------------------------------

    elements = page.locator(
        "input, textarea, select"
    )

    count = await elements.count()

    for index in range(
        min(
            count,
            150,
        )
    ):
        element = elements.nth(index)

        try:
            input_type = normalize(
                await element.get_attribute(
                    "type"
                )
                or ""
            )

            if input_type in [
                "hidden",
                "submit",
                "button",
                "checkbox",
                "radio",
                "file",
            ]:
                continue

            tag_name = await element.evaluate(
                "(el) => el.tagName.toLowerCase()"
            )

            context = await get_field_context(
                element
            )

            if not context:
                continue

            required = await field_is_required(
                element,
                context,
            )

            if (
                classify_field_context(
                    context,
                    required,
                )
                != "safe"
            ):
                continue

            value = None
            field_name = None

            if any(
                x in context
                for x in [
                    "preferred first name",
                    "preferred name",
                ]
            ):
                value = request.first_name
                field_name = (
                    "Preferred first name"
                )

            elif any(
                x in context
                for x in [
                    "first name",
                    "firstname",
                    "given name",
                ]
            ):
                value = request.first_name
                field_name = "First name"

            elif any(
                x in context
                for x in [
                    "last name",
                    "lastname",
                    "surname",
                    "family name",
                ]
            ):
                value = request.last_name
                field_name = "Last name"

            elif (
                "full name" in context
                or context == "name"
            ):
                value = (
                    request.full_name
                    or (
                        f"{request.first_name} "
                        f"{request.last_name}"
                    ).strip()
                )

                field_name = "Full name"

            elif "email" in context:
                value = request.email
                field_name = "Email"

            elif any(
                x in context
                for x in [
                    "phone",
                    "telephone",
                    "mobile",
                ]
            ):
                value = request.phone
                field_name = "Phone"

            elif any(
                x in context
                for x in [
                    "current country of residence",
                    "country of residence",
                    "country off country",
                    "country in which you are located",
                ]
            ):
                value = request.country
                field_name = "Country"

            if not value:
                continue

            # Don't repeatedly overwrite fields
            # already populated above.
            try:
                existing = await element.input_value()

                if existing.strip():
                    continue

            except Exception:
                pass

            if tag_name == "select":
                try:
                    await element.select_option(
                        label=value
                    )

                    filled.append(
                        field_name
                    )

                    continue

                except Exception:
                    try:
                        await element.select_option(
                            value=value
                        )

                        filled.append(
                            field_name
                        )

                        continue

                    except Exception:
                        skipped.append(
                            context
                        )

                        continue

            try:
                await element.fill(
                    str(value)
                )

                filled.append(
                    field_name
                )

            except Exception:
                skipped.append(
                    context
                )

        except Exception:
            continue

    # Give React-style forms time to process
    # their input/change events.
    await page.wait_for_timeout(
        800
    )

    return {
        "filled":
            list(
                dict.fromkeys(
                    filled
                )
            ),

        "skipped":
            list(
                dict.fromkeys(
                    skipped
                )
            ),
    }


async def upload_resume(
    page: Page,
    role_type,
):
    resume_path = (
        get_resume_path(
            role_type
        )
    )

    if resume_path is None:
        return {
            "uploaded": False,
            "reason":
                "Configured resume could not be found.",
        }

    file_inputs = page.locator(
        'input[type="file"]'
    )

    count = (
        await file_inputs.count()
    )

    if count == 0:
        return {
            "uploaded": False,
            "reason":
                "No resume upload field was detected.",
        }

    for index in range(count):
        element = (
            file_inputs.nth(index)
        )

        context = (
            await get_field_context(
                element
            )
        )

        if any(
            keyword in context
            for keyword in [
                "resume",
                "cv",
                "curriculum",
            ]
        ):
            try:
                await element.set_input_files(
                    str(
                        resume_path
                    )
                )

                return {
                    "uploaded": True,
                    "filename":
                        resume_path.name,
                }

            except Exception as error:
                return {
                    "uploaded": False,
                    "reason":
                        str(error),
                }

    if count == 1:
        try:
            await (
                file_inputs.first
                .set_input_files(
                    str(
                        resume_path
                    )
                )
            )

            return {
                "uploaded": True,
                "filename":
                    resume_path.name,
            }

        except Exception as error:
            return {
                "uploaded": False,
                "reason": str(error),
            }

    return {
        "uploaded": False,
        "reason":
            (
                "Multiple upload fields detected "
                "and Roleza could not safely identify "
                "the resume field."
            ),
    }


@router.get("/test")
async def test_browser():
    async with (
        async_playwright()
        as playwright
    ):
        browser = (
            await playwright
            .chromium
            .launch(
                headless=True
            )
        )

        page = (
            await browser.new_page()
        )

        await page.goto(
            "https://example.com",
            wait_until="domcontentloaded",
            timeout=30000,
        )

        title = await page.title()

        await browser.close()

    return {
        "success": True,
        "title": title,
    }


@router.post(
    "/inspect-application"
)
async def inspect_application(
    request: InspectApplicationRequest,
):
    if not validate_url(
        request.job_url
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid job URL.",
        )

    async with (
        async_playwright()
        as playwright
    ):
        browser = (
            await playwright
            .chromium
            .launch(
                headless=True
            )
        )

        context = (
            await browser.new_context()
        )

        page = (
            await context.new_page()
        )

        try:
            await page.goto(
                request.job_url,
                wait_until="domcontentloaded",
                timeout=45000,
            )

            await page.wait_for_timeout(
                1500
            )

            original_url = page.url

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead["dead"]:
                return {
                    "success": False,
                    "dead_job": True,
                    "status": "Dead job",
                    "dead_job_reason":
                        dead["reason"],
                    "original_url":
                        original_url,
                    "current_url":
                        page.url,
                    "recommended_action":
                        "Remove from results",
                }

            application_result = (
                await click_apply_and_follow(
                    page
                )
            )

            page = (
                application_result[
                    "page"
                ]
            )

            await page.wait_for_timeout(
                1500
            )

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead["dead"]:
                return {
                    "success": False,
                    "dead_job": True,
                    "status": "Dead job",
                    "dead_job_reason":
                        dead["reason"],
                    "original_url":
                        original_url,
                    "current_url":
                        page.url,
                    "application_form_opened":
                        application_result[
                            "opened"
                        ],
                    "new_tab_opened":
                        application_result[
                            "new_tab"
                        ],
                    "recommended_action":
                        "Remove from results",
                }

            captcha = (
                await detect_captcha(
                    page
                )
            )

            login_wall = (
                await detect_login_wall(
                    page
                )
            )

            fields = (
                await inspect_fields(
                    page
                )
            )

            summary = (
                build_field_summary(
                    fields,
                    captcha,
                    login_wall,
                )
            )

            if summary[
                "hard_blockers"
            ]:
                action = (
                    "Human action required"
                )

            elif summary[
                "user_decisions"
            ]:
                action = (
                    "User answers required"
                )

            elif summary[
                "unknown_required_fields"
            ]:
                action = (
                    "Review unknown required fields"
                )

            elif summary[
                "draftable_questions"
            ]:
                action = (
                    "Roleza can draft answers for review"
                )

            else:
                action = (
                    "Safe to prepare application"
                )

            return {
                "success": True,
                "dead_job": False,
                "original_url":
                    original_url,
                "current_url":
                    page.url,

                "application_form_opened":
                    application_result[
                        "opened"
                    ],

                "new_tab_opened":
                    application_result[
                        "new_tab"
                    ],

                "captcha_detected":
                    captcha,

                "login_detected":
                    login_wall,

                "fields_detected":
                    len(fields),

                "summary":
                    summary,

                "recommended_action":
                    action,
            }

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=str(error),
            )

        finally:
            await browser.close()


@router.post(
    "/start-application"
)
async def start_application(
    request: StartApplicationRequest,
):
    request = (
        apply_saved_profile(
            request
        )
    )

    if not validate_url(
        request.job_url
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid job URL.",
        )

    async with (
        async_playwright()
        as playwright
    ):
        browser = (
            await playwright
            .chromium
            .launch(
                headless=False
            )
        )

        context = (
            await browser.new_context()
        )

        page = (
            await context.new_page()
        )

        try:
            await page.goto(
                request.job_url,
                wait_until="domcontentloaded",
                timeout=45000,
            )

            await page.wait_for_timeout(
                1500
            )

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead["dead"]:
                return {
                    "success": False,
                    "dead_job": True,
                    "status": "Dead job",
                    "dead_job_reason":
                        dead["reason"],
                    "current_url":
                        page.url,
                    "submitted": False,
                }

            application_result = (
                await click_apply_and_follow(
                    page
                )
            )

            page = (
                application_result[
                    "page"
                ]
            )

            await page.wait_for_timeout(
                1500
            )

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead["dead"]:
                return {
                    "success": False,
                    "dead_job": True,
                    "status": "Dead job",
                    "dead_job_reason":
                        dead["reason"],
                    "current_url":
                        page.url,
                    "new_tab_opened":
                        application_result[
                            "new_tab"
                        ],
                    "submitted": False,
                }

            captcha = (
                await detect_captcha(
                    page
                )
            )

            login_wall = (
                await detect_login_wall(
                    page
                )
            )

            fields = (
                await inspect_fields(
                    page
                )
            )

            summary = (
                build_field_summary(
                    fields,
                    captcha,
                    login_wall,
                )
            )

            if summary[
                "hard_blockers"
            ]:
                return {
                    "success": False,

                    "status":
                        "Needs human action",

                    "dead_job": False,

                    "hard_blockers":
                        summary[
                            "hard_blockers"
                        ],

                    "draftable_questions":
                        summary[
                            "draftable_questions"
                        ],

                    "user_decisions":
                        summary[
                            "user_decisions"
                        ],

                    "personal_questions":
                        summary[
                            "personal_questions"
                        ],

                    "unknown_required_fields":
                        summary[
                            "unknown_required_fields"
                        ],

                    "current_url":
                        page.url,

                    "new_tab_opened":
                        application_result[
                            "new_tab"
                        ],

                    "submitted":
                        False,
                }

            fill_result = (
                await safe_fill(
                    page,
                    request,
                )
            )

            resume_result = (
                await upload_resume(
                    page,
                    request.role_type,
                )
            )

            await page.wait_for_timeout(
                1500
            )

            fields_after = (
                await inspect_fields(
                    page
                )
            )

            summary_after = (
                build_field_summary(
                    fields_after,
                    False,
                    False,
                )
            )

            return {
                "success": True,

                "status":
                    "Prepared for review",

                "dead_job": False,

                "current_url":
                    page.url,

                "new_tab_opened":
                    application_result[
                        "new_tab"
                    ],

                "filled_fields":
                    fill_result[
                        "filled"
                    ],

                "skipped_fields":
                    fill_result[
                        "skipped"
                    ],

                "resume":
                    resume_result,

                "draftable_questions":
                    summary_after[
                        "draftable_questions"
                    ],

                "user_decisions":
                    summary_after[
                        "user_decisions"
                    ],

                "personal_questions":
                    summary_after[
                        "personal_questions"
                    ],

                "unknown_required_fields":
                    summary_after[
                        "unknown_required_fields"
                    ],

                "submitted": False,
            }

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Browser automation failed: "
                    f"{error}"
                ),
            )

        finally:
            # Temporary debugging:
            # leave browser open for 60 seconds.
            try:
                await page.wait_for_timeout(
                    60000
                )
            except Exception:
                pass

            try:
                await browser.close()
            except Exception:
                pass