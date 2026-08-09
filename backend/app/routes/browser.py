from pathlib import Path
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from playwright.async_api import (
    Page,
    Frame,
    async_playwright,
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

RESUME_DIR = (
    BASE_DIR
    / "resumes"
)

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


# =========================================================
# FIELD CLASSIFICATION
# =========================================================

SAFE_FIELD_KEYWORDS = [
    "first name",
    "firstname",
    "given name",
    "preferred first name",
    "preferred name",
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

    "do you currently live in this location",
    "currently live in this location",
    "open to candidates in",
    "currently reside in",
    "currently living in",

    "years of professional software engineering experience",
    "years of software engineering experience",
    "do you have over",
    "rate yourself",
    "scale from 0 to 5",
    "scale from 1 to 5",

    "employment agreements",
    "post-employment restrictions",
    "post employment restrictions",
    "previously worked at",
    "previously worked for",
    "previously consulted for",
    "worked at or consulted for",

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
    "apply to this job",
    "apply for this position",
    "apply to this position",
    "apply here",
    "start application",
    "apply",
]


# =========================================================
# REQUEST MODELS
# =========================================================

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


# =========================================================
# BASIC HELPERS
# =========================================================

def normalize(
    value,
):
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


def validate_url(
    job_url,
):
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


# =========================================================
# PAGE STATUS
# =========================================================

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
    """
    Detect CAPTCHA on the main page
    OR any iframe.

    Important for Greenhouse forms.
    """

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

    for frame in page.frames:
        frame_url = normalize(
            frame.url
        )

        if any(
            keyword in frame_url
            for keyword in [
                "recaptcha",
                "hcaptcha",
                "captcha",
            ]
        ):
            return True

        try:
            if (
                await frame.locator(
                    "[data-sitekey]"
                ).count()
                > 0
            ):
                return True

        except Exception:
            pass

    return False


async def detect_login_wall(
    page: Page,
):
    scopes = [
        page,
        *page.frames,
    ]

    for scope in scopes:
        try:
            if (
                await scope.locator(
                    'input[type="password"]'
                ).count()
                > 0
            ):
                return True

        except Exception:
            pass

    return False


# =========================================================
# APPLICATION FRAME DETECTION
# =========================================================

def is_noise_frame(
    frame: Frame,
):
    url = normalize(
        frame.url
    )

    noise = [
        "recaptcha",
        "hcaptcha",
        "captcha",
        "content.googleapis.com/static/proxy",
    ]

    return any(
        item in url
        for item in noise
    )


async def count_meaningful_fields(
    scope,
):
    """
    Count real application controls.

    Hidden CAPTCHA/system fields
    are ignored.
    """

    try:
        elements = scope.locator(
            "input, textarea, select"
        )

        count = (
            await elements.count()
        )

    except Exception:
        return 0

    meaningful = 0

    for index in range(
        min(
            count,
            250,
        )
    ):
        element = (
            elements.nth(
                index
            )
        )

        try:
            input_type = normalize(
                await element.get_attribute(
                    "type"
                )
                or ""
            )

            if input_type == "hidden":
                continue

            meaningful += 1

        except Exception:
            meaningful += 1

    return meaningful


async def get_application_scope(
    page: Page,
):
    """
    Find where the actual application form lives.

    It may be:
    - directly on the page
    - inside a Greenhouse iframe
    - inside another ATS iframe
    """

    best_scope = page

    best_count = (
        await count_meaningful_fields(
            page
        )
    )

    best_url = page.url
    best_is_frame = False

    for frame in page.frames:
        if frame == page.main_frame:
            continue

        if is_noise_frame(
            frame
        ):
            continue

        count = (
            await count_meaningful_fields(
                frame
            )
        )

        if count > best_count:
            best_scope = frame
            best_count = count
            best_url = frame.url
            best_is_frame = True

    return {
        "scope":
            best_scope,

        "field_count":
            best_count,

        "scope_url":
            best_url,

        "is_frame":
            best_is_frame,
    }


async def wait_for_application_scope(
    page: Page,
    timeout_ms=15000,
):
    elapsed = 0

    while elapsed < timeout_ms:
        result = (
            await get_application_scope(
                page
            )
        )

        if (
            result[
                "field_count"
            ]
            > 0
        ):
            return result

        await page.wait_for_timeout(
            500
        )

        elapsed += 500

    return (
        await get_application_scope(
            page
        )
    )


# =========================================================
# APPLY LINK / POPUP ROUTING
# =========================================================

async def click_apply_and_follow(
    page: Page,
):
    """
    Follow real employer application destination.

    Supports:
    - direct href
    - redirects
    - popup/new-tab ATS pages
    """

    context = page.context

    # -------------------------------------------------
    # DIRECT APPLY LINK
    # -------------------------------------------------

    for text in APPLY_BUTTON_TEXT:
        pattern = re.compile(
            rf"^{re.escape(text)}$",
            re.IGNORECASE,
        )

        try:
            links = (
                page.get_by_role(
                    "link",
                    name=pattern,
                )
            )

            count = (
                await links.count()
            )

            for index in range(
                count
            ):
                link = (
                    links.nth(
                        index
                    )
                )

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

                absolute_url = (
                    await link.evaluate(
                        "(el) => el.href"
                    )
                )

                if (
                    not absolute_url
                    or absolute_url
                    == page.url
                ):
                    continue

                application_page = (
                    await context.new_page()
                )

                await application_page.goto(
                    absolute_url,
                    wait_until=
                        "domcontentloaded",
                    timeout=45000,
                )

                await application_page.wait_for_timeout(
                    2500
                )

                return {
                    "opened":
                        True,

                    "page":
                        application_page,

                    "new_tab":
                        True,

                    "method":
                        "direct_href",

                    "application_url":
                        application_page.url,
                }

        except Exception:
            pass

    # -------------------------------------------------
    # CLICK APPLY / CAPTURE POPUP
    # -------------------------------------------------

    for text in APPLY_BUTTON_TEXT:
        pattern = re.compile(
            rf"^{re.escape(text)}$",
            re.IGNORECASE,
        )

        candidates = []

        try:
            button = (
                page.get_by_role(
                    "button",
                    name=pattern,
                )
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
            link = (
                page.get_by_role(
                    "link",
                    name=pattern,
                )
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

                old_url = (
                    page.url
                )

                try:
                    async with (
                        context.expect_page(
                            timeout=10000
                        )
                    ) as popup_info:

                        await candidate.click()

                    popup = (
                        await popup_info.value
                    )

                    try:
                        await popup.wait_for_load_state(
                            "domcontentloaded",
                            timeout=30000,
                        )

                    except Exception:
                        pass

                    await popup.wait_for_timeout(
                        2500
                    )

                    return {
                        "opened":
                            True,

                        "page":
                            popup,

                        "new_tab":
                            True,

                        "method":
                            "popup",

                        "application_url":
                            popup.url,
                    }

                except Exception:
                    pass

                await page.wait_for_timeout(
                    4000
                )

                pages_after = list(
                    context.pages
                )

                new_pages = [
                    p
                    for p in pages_after
                    if p not in pages_before
                ]

                if new_pages:
                    popup = (
                        new_pages[-1]
                    )

                    return {
                        "opened":
                            True,

                        "page":
                            popup,

                        "new_tab":
                            True,

                        "method":
                            "popup_fallback",

                        "application_url":
                            popup.url,
                    }

                if page.url != old_url:
                    return {
                        "opened":
                            True,

                        "page":
                            page,

                        "new_tab":
                            False,

                        "method":
                            "same_tab_redirect",

                        "application_url":
                            page.url,
                    }

            except Exception:
                continue

    return {
        "opened":
            False,

        "page":
            page,

        "new_tab":
            False,

        "method":
            "not_found",

        "application_url":
            page.url,
    }


# =========================================================
# FIELD CONTEXT
# =========================================================

async def get_field_context(
    element,
):
    """
    Build field context using DOM inside
    the field's own page/frame.

    This is iframe-safe.
    """

    try:
        parts = (
            await element.evaluate(
                """
                (el) => {
                    const output = [];

                    const attrs = [
                        'name',
                        'id',
                        'placeholder',
                        'aria-label',
                        'autocomplete',
                        'data-automation-id',
                        'data-testid'
                    ];

                    for (const attr of attrs) {
                        const value =
                            el.getAttribute(attr);

                        if (value) {
                            output.push(value);
                        }
                    }

                    if (el.labels) {
                        for (
                            const label
                            of Array.from(
                                el.labels
                            )
                        ) {
                            const text =
                                (
                                    label.innerText
                                    ||
                                    label.textContent
                                    ||
                                    ''
                                ).trim();

                            if (text) {
                                output.push(
                                    text
                                );
                            }
                        }
                    }

                    const labelledBy =
                        el.getAttribute(
                            'aria-labelledby'
                        );

                    if (labelledBy) {
                        for (
                            const id
                            of labelledBy.split(
                                /\\s+/
                            )
                        ) {
                            const node =
                                el.ownerDocument
                                .getElementById(
                                    id
                                );

                            if (node) {
                                const text =
                                    (
                                        node.innerText
                                        ||
                                        node.textContent
                                        ||
                                        ''
                                    ).trim();

                                if (text) {
                                    output.push(
                                        text
                                    );
                                }
                            }
                        }
                    }

                    const wrapped =
                        el.closest(
                            'label'
                        );

                    if (wrapped) {
                        const text =
                            (
                                wrapped.innerText
                                ||
                                wrapped.textContent
                                ||
                                ''
                            ).trim();

                        if (text) {
                            output.push(
                                text
                            );
                        }
                    }

                    if (el.id) {
                        try {
                            const escaped =
                                CSS.escape(
                                    el.id
                                );

                            const label =
                                el.ownerDocument
                                .querySelector(
                                    `label[for="${escaped}"]`
                                );

                            if (label) {
                                const text =
                                    (
                                        label.innerText
                                        ||
                                        label.textContent
                                        ||
                                        ''
                                    ).trim();

                                if (text) {
                                    output.push(
                                        text
                                    );
                                }
                            }

                        } catch (e) {}
                    }

                    return output;
                }
                """
            )
        )

    except Exception:
        parts = []

    return normalize(
        " ".join(
            str(part)
            for part in parts
            if part
        )
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


# =========================================================
# FIELD INSPECTION
# =========================================================

async def inspect_fields(
    scope,
):
    results = []

    elements = (
        scope.locator(
            "input, textarea, select"
        )
    )

    count = (
        await elements.count()
    )

    for index in range(
        min(
            count,
            250,
        )
    ):
        element = (
            elements.nth(
                index
            )
        )

        try:
            input_type = normalize(
                await element.get_attribute(
                    "type"
                )
                or ""
            )

            if input_type == "hidden":
                continue

            tag_name = (
                await element.evaluate(
                    "(el) => "
                    "el.tagName.toLowerCase()"
                )
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
                    "index":
                        index,

                    "type":
                        (
                            input_type
                            or tag_name
                        ),

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


# =========================================================
# SUMMARY
# =========================================================

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
        category = (
            field.get(
                "category"
            )
        )

        if category == "safe":
            safe_fields.append(
                field
            )

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

        elif (
            category
            == "unknown_required"
        ):
            unknown_required.append(
                field
            )

        elif (
            category
            == "unknown_optional"
        ):
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

    if not fields:
        hard_blockers.append(
            "Application form not detected"
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
                len(
                    safe_fields
                ),

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

        # CAPTCHA does NOT stop Roleza
        # from preparing safe fields.
        #
        # It only stops submission.
        "can_prepare_application":
            (
                bool(fields)
                and not login_wall
            ),

        "can_submit_automatically":
            (
                bool(fields)
                and not hard_blockers
                and not user_decisions
                and not personal_questions
                and not draftable_questions
                and not unknown_required
            ),
    }


# =========================================================
# SAFE AUTOFILL
# =========================================================

async def safe_fill(
    scope,
    request: StartApplicationRequest,
):
    filled = []
    skipped = []

    def remember_filled(
        name,
    ):
        if (
            name
            and name not in filled
        ):
            filled.append(
                name
            )

    def remember_skipped(
        name,
    ):
        if (
            name
            and name not in skipped
        ):
            skipped.append(
                name
            )

    async def try_fill(
        locator,
        value,
        field_name,
    ):
        if not value:
            return False

        try:
            count = (
                await locator.count()
            )

        except Exception:
            return False

        for index in range(
            min(
                count,
                15,
            )
        ):
            element = (
                locator.nth(
                    index
                )
            )

            try:
                if not (
                    await element.is_visible()
                ):
                    continue

            except Exception:
                pass

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

            except Exception:
                pass

            try:
                existing = (
                    await element.input_value()
                )

                if existing.strip():
                    remember_filled(
                        field_name
                    )

                    return True

            except Exception:
                pass

            try:
                await element.fill(
                    str(value)
                )

                existing = (
                    await element.input_value()
                )

                if existing.strip():
                    remember_filled(
                        field_name
                    )

                    return True

            except Exception:
                pass

            # React / custom controlled input fallback
            try:
                await element.evaluate(
                    """
                    (el, value) => {
                        const proto =
                            Object.getPrototypeOf(
                                el
                            );

                        const descriptor =
                            Object.getOwnPropertyDescriptor(
                                proto,
                                'value'
                            );

                        if (
                            descriptor
                            &&
                            descriptor.set
                        ) {
                            descriptor.set.call(
                                el,
                                value
                            );
                        } else {
                            el.value = value;
                        }

                        el.dispatchEvent(
                            new Event(
                                'input',
                                {
                                    bubbles: true
                                }
                            )
                        );

                        el.dispatchEvent(
                            new Event(
                                'change',
                                {
                                    bubbles: true
                                }
                            )
                        );

                        el.dispatchEvent(
                            new Event(
                                'blur',
                                {
                                    bubbles: true
                                }
                            )
                        );
                    }
                    """,
                    str(value),
                )

                remember_filled(
                    field_name
                )

                return True

            except Exception:
                continue

        return False


    async def fill_field(
        field_name,
        value,
        patterns,
        selectors,
    ):
        if not value:
            remember_skipped(
                (
                    f"{field_name}: "
                    "no saved value"
                )
            )

            return False

        for pattern in patterns:
            try:
                if await try_fill(
                    scope.get_by_role(
                        "textbox",
                        name=re.compile(
                            pattern,
                            re.IGNORECASE,
                        ),
                    ),
                    value,
                    field_name,
                ):
                    return True

            except Exception:
                pass

        for pattern in patterns:
            try:
                if await try_fill(
                    scope.get_by_label(
                        re.compile(
                            pattern,
                            re.IGNORECASE,
                        )
                    ),
                    value,
                    field_name,
                ):
                    return True

            except Exception:
                pass

        for selector in selectors:
            try:
                if await try_fill(
                    scope.locator(
                        selector
                    ),
                    value,
                    field_name,
                ):
                    return True

            except Exception:
                pass

        remember_skipped(
            (
                f"{field_name}: "
                "field not matched"
            )
        )

        return False


    # -------------------------------------------------
    # PREFERRED NAME
    # -------------------------------------------------

    await fill_field(
        "Preferred first name",
        request.first_name,
        [
            r"^\s*preferred\s+first\s+name\b",
            r"^\s*preferred\s+name\b",
        ],
        [
            'input[name*="preferred" i]',
            'input[id*="preferred" i]',
        ],
    )


    # -------------------------------------------------
    # FIRST NAME
    # -------------------------------------------------

    await fill_field(
        "First name",
        request.first_name,
        [
            r"^\s*first\s+name\b",
            r"^\s*given\s+name\b",
        ],
        [
            'input[id="first_name" i]',
            'input[name="first_name" i]',
            'input[autocomplete="given-name"]',
            'input[name*="first_name" i]',
            'input[id*="first_name" i]',
        ],
    )


    # -------------------------------------------------
    # LAST NAME
    # -------------------------------------------------

    await fill_field(
        "Last name",
        request.last_name,
        [
            r"^\s*last\s+name\b",
            r"^\s*surname\b",
            r"^\s*family\s+name\b",
        ],
        [
            'input[id="last_name" i]',
            'input[name="last_name" i]',
            'input[autocomplete="family-name"]',
            'input[name*="last_name" i]',
            'input[id*="last_name" i]',
        ],
    )


    # -------------------------------------------------
    # FULL NAME
    # -------------------------------------------------

    full_name = (
        request.full_name
        or (
            f"{request.first_name} "
            f"{request.last_name}"
        ).strip()
    )

    await fill_field(
        "Full name",
        full_name,
        [
            r"^\s*full\s+name\b",
            r"^\s*name\s*\*?\s*$",
        ],
        [
            'input[autocomplete="name"]',
            'input[name="name" i]',
            'input[id="name" i]',
            'input[name*="systemfield_name" i]',
            'input[id*="systemfield_name" i]',
        ],
    )


    # -------------------------------------------------
    # EMAIL
    # -------------------------------------------------

    await fill_field(
        "Email",
        request.email,
        [
            r"^\s*email\b",
            r"^\s*email\s+address\b",
        ],
        [
            'input[id="email" i]',
            'input[name="email" i]',
            'input[type="email"]',
            'input[autocomplete="email"]',
            'input[name*="email" i]',
            'input[id*="email" i]',
        ],
    )


    # -------------------------------------------------
    # PHONE
    # -------------------------------------------------

    await fill_field(
        "Phone",
        request.phone,
        [
            r"^\s*phone\b",
            r"^\s*telephone\b",
            r"^\s*mobile\b",
        ],
        [
            'input[id="phone" i]',
            'input[name="phone" i]',
            'input[type="tel"]',
            'input[autocomplete="tel"]',
            'input[name*="phone" i]',
            'input[id*="phone" i]',
        ],
    )


    # =================================================
    # COUNTRY
    # =================================================

    country_done = False

    if request.country:
        country_patterns = [
            r"^\s*country\s*\*?\s*$",
            r"country\s+of\s+residence",
            r"current\s+country\s+of\s+residence",
        ]

        # ---------------------------------------------
        # NORMAL SELECT
        # ---------------------------------------------

        for pattern in country_patterns:
            try:
                locator = (
                    scope.get_by_label(
                        re.compile(
                            pattern,
                            re.IGNORECASE,
                        )
                    )
                )

                count = (
                    await locator.count()
                )

                for index in range(
                    min(
                        count,
                        10,
                    )
                ):
                    element = (
                        locator.nth(
                            index
                        )
                    )

                    try:
                        tag_name = (
                            await element.evaluate(
                                "(el) => "
                                "el.tagName.toLowerCase()"
                            )
                        )

                    except Exception:
                        tag_name = ""

                    if tag_name != "select":
                        continue

                    try:
                        await element.select_option(
                            label=
                                request.country
                        )

                        remember_filled(
                            "Country"
                        )

                        country_done = True

                        break

                    except Exception:
                        try:
                            await element.select_option(
                                value=
                                    request.country
                            )

                            remember_filled(
                                "Country"
                            )

                            country_done = True

                            break

                        except Exception:
                            pass

                if country_done:
                    break

            except Exception:
                pass


        # ---------------------------------------------
        # GREENHOUSE / CUSTOM COMBOBOX
        # ---------------------------------------------

        if not country_done:
            try:
                country_input = (
                    scope.locator(
                        'input[id="country"]'
                    )
                )

                if (
                    await country_input.count()
                    > 0
                ):
                    element = (
                        country_input.first
                    )

                    await element.click()

                    try:
                        await element.fill(
                            request.country
                        )

                    except Exception:
                        pass

                    try:
                        option = (
                            scope.get_by_role(
                                "option",
                                name=re.compile(
                                    rf"^\s*"
                                    rf"{re.escape(request.country)}"
                                    rf"\s*$",
                                    re.IGNORECASE,
                                ),
                            )
                        )

                        if (
                            await option.count()
                            > 0
                        ):
                            await option.first.click()

                            remember_filled(
                                "Country"
                            )

                            country_done = True

                    except Exception:
                        pass

            except Exception:
                pass


        if not country_done:
            for pattern in country_patterns:
                try:
                    combo = (
                        scope.get_by_role(
                            "combobox",
                            name=re.compile(
                                pattern,
                                re.IGNORECASE,
                            ),
                        )
                    )

                    if (
                        await combo.count()
                        == 0
                    ):
                        continue

                    element = (
                        combo.first
                    )

                    await element.click()

                    try:
                        await element.fill(
                            request.country
                        )

                    except Exception:
                        pass

                    option = (
                        scope.get_by_text(
                            re.compile(
                                rf"^\s*"
                                rf"{re.escape(request.country)}"
                                rf"\s*$",
                                re.IGNORECASE,
                            )
                        )
                    )

                    if (
                        await option.count()
                        > 0
                    ):
                        await option.last.click()

                        remember_filled(
                            "Country"
                        )

                        country_done = True

                        break

                except Exception:
                    pass


        if not country_done:
            remember_skipped(
                "Country: field not matched"
            )


    return {
        "filled":
            filled,

        "skipped":
            skipped,
    }


# =========================================================
# RESUME UPLOAD
# =========================================================

async def upload_resume(
    scope,
    role_type,
):
    resume_path = (
        get_resume_path(
            role_type
        )
    )

    if resume_path is None:
        return {
            "uploaded":
                False,

            "reason":
                (
                    "Configured resume "
                    "could not be found."
                ),
        }

    file_inputs = (
        scope.locator(
            'input[type="file"]'
        )
    )

    count = (
        await file_inputs.count()
    )

    if count == 0:
        return {
            "uploaded":
                False,

            "reason":
                (
                    "No resume upload "
                    "field was detected."
                ),
        }

    # Try to identify resume field
    for index in range(
        count
    ):
        element = (
            file_inputs.nth(
                index
            )
        )

        context = (
            await get_field_context(
                element
            )
        )

        if contains_any(
            context,
            [
                "resume",
                "cv",
                "curriculum",
            ],
        ):
            try:
                await element.set_input_files(
                    str(
                        resume_path
                    )
                )

                return {
                    "uploaded":
                        True,

                    "filename":
                        resume_path.name,
                }

            except Exception as error:
                return {
                    "uploaded":
                        False,

                    "reason":
                        str(error),
                }


    # Greenhouse often places Resume first
    if count >= 1:
        first = (
            file_inputs.first
        )

        first_context = (
            await get_field_context(
                first
            )
        )

        if (
            "cover" not in first_context
            and "letter" not in first_context
        ):
            try:
                await first.set_input_files(
                    str(
                        resume_path
                    )
                )

                return {
                    "uploaded":
                        True,

                    "filename":
                        resume_path.name,
                }

            except Exception:
                pass


    return {
        "uploaded":
            False,

        "reason":
            (
                "Roleza could not safely "
                "identify the resume field."
            ),
    }


# =========================================================
# TEST
# =========================================================

@router.get(
    "/test"
)
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
            wait_until=
                "domcontentloaded",
            timeout=30000,
        )

        title = (
            await page.title()
        )

        await browser.close()

    return {
        "success":
            True,

        "title":
            title,
    }


# =========================================================
# INSPECT APPLICATION
# =========================================================

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
            detail=
                "Invalid job URL.",
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
                wait_until=
                    "domcontentloaded",
                timeout=45000,
            )

            await page.wait_for_timeout(
                1500
            )

            original_url = (
                page.url
            )

            # -----------------------------------------
            # DEAD JOB CHECK
            # -----------------------------------------

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead[
                "dead"
            ]:
                return {
                    "success":
                        False,

                    "dead_job":
                        True,

                    "status":
                        "Dead job",

                    "dead_job_reason":
                        dead[
                            "reason"
                        ],

                    "original_url":
                        original_url,

                    "current_url":
                        page.url,

                    "recommended_action":
                        "Remove from results",
                }


            # -----------------------------------------
            # FOLLOW REAL ATS
            # -----------------------------------------

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
                2000
            )


            # -----------------------------------------
            # FIND APPLICATION FRAME
            # -----------------------------------------

            scope_result = (
                await wait_for_application_scope(
                    page
                )
            )

            application_scope = (
                scope_result[
                    "scope"
                ]
            )


            # -----------------------------------------
            # DEAD JOB AGAIN
            # -----------------------------------------

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead[
                "dead"
            ]:
                return {
                    "success":
                        False,

                    "dead_job":
                        True,

                    "status":
                        "Dead job",

                    "dead_job_reason":
                        dead[
                            "reason"
                        ],

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


            # -----------------------------------------
            # BLOCKERS
            # -----------------------------------------

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


            # -----------------------------------------
            # INSPECT ACTUAL APPLICATION SCOPE
            # -----------------------------------------

            fields = (
                await inspect_fields(
                    application_scope
                )
            )

            summary = (
                build_field_summary(
                    fields,
                    captcha,
                    login_wall,
                )
            )


            # -----------------------------------------
            # RECOMMENDED ACTION
            # -----------------------------------------

            if not fields:
                action = (
                    "Human action required"
                )

            elif (
                summary[
                    "hard_blockers"
                ]
            ):
                action = (
                    "Human action required"
                )

            elif (
                summary[
                    "user_decisions"
                ]
            ):
                action = (
                    "User answers required"
                )

            elif (
                summary[
                    "unknown_required_fields"
                ]
            ):
                action = (
                    "Review unknown required fields"
                )

            elif (
                summary[
                    "draftable_questions"
                ]
            ):
                action = (
                    "Roleza can draft answers for review"
                )

            else:
                action = (
                    "Safe to prepare application"
                )


            return {
                "success":
                    True,

                "dead_job":
                    False,

                "original_url":
                    original_url,

                "current_url":
                    page.url,

                "application_scope_url":
                    scope_result[
                        "scope_url"
                    ],

                "application_in_iframe":
                    scope_result[
                        "is_frame"
                    ],

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
                    len(
                        fields
                    ),

                "summary":
                    summary,

                "recommended_action":
                    action,
            }


        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=
                    str(
                        error
                    ),
            )


        finally:
            await browser.close()


# =========================================================
# PREPARE APPLICATION
# =========================================================

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
            detail=
                "Invalid job URL.",
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
                wait_until=
                    "domcontentloaded",
                timeout=45000,
            )

            await page.wait_for_timeout(
                1500
            )


            # -----------------------------------------
            # DEAD JOB
            # -----------------------------------------

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead[
                "dead"
            ]:
                return {
                    "success":
                        False,

                    "dead_job":
                        True,

                    "status":
                        "Dead job",

                    "dead_job_reason":
                        dead[
                            "reason"
                        ],

                    "current_url":
                        page.url,

                    "submitted":
                        False,
                }


            # -----------------------------------------
            # FOLLOW ATS
            # -----------------------------------------

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
                2000
            )


            # -----------------------------------------
            # FIND REAL FORM / IFRAME
            # -----------------------------------------

            scope_result = (
                await wait_for_application_scope(
                    page
                )
            )

            application_scope = (
                scope_result[
                    "scope"
                ]
            )


            # -----------------------------------------
            # DEAD JOB AGAIN
            # -----------------------------------------

            dead = (
                await detect_dead_job(
                    page
                )
            )

            if dead[
                "dead"
            ]:
                return {
                    "success":
                        False,

                    "dead_job":
                        True,

                    "status":
                        "Dead job",

                    "dead_job_reason":
                        dead[
                            "reason"
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
                    application_scope
                )
            )

            summary = (
                build_field_summary(
                    fields,
                    captcha,
                    login_wall,
                )
            )


            # -----------------------------------------
            # FORM MISSING / LOGIN
            # -----------------------------------------

            if (
                not fields
                or login_wall
            ):
                return {
                    "success":
                        False,

                    "status":
                        "Needs human action",

                    "dead_job":
                        False,

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

                    "application_scope_url":
                        scope_result[
                            "scope_url"
                        ],

                    "application_in_iframe":
                        scope_result[
                            "is_frame"
                        ],

                    "new_tab_opened":
                        application_result[
                            "new_tab"
                        ],

                    "submitted":
                        False,
                }


            # =================================================
            # IMPORTANT:
            #
            # CAPTCHA DOES NOT STOP PREPARATION.
            #
            # Roleza may safely fill name/email/phone/country/
            # resume.
            #
            # It still NEVER solves/bypasses CAPTCHA
            # and NEVER submits through CAPTCHA.
            # =================================================


            fill_result = (
                await safe_fill(
                    application_scope,
                    request,
                )
            )


            resume_result = (
                await upload_resume(
                    application_scope,
                    request.role_type,
                )
            )


            await page.wait_for_timeout(
                1500
            )


            fields_after = (
                await inspect_fields(
                    application_scope
                )
            )


            summary_after = (
                build_field_summary(
                    fields_after,
                    captcha,
                    login_wall,
                )
            )


            if captcha:
                status = (
                    "Prepared - human verification required"
                )

            else:
                status = (
                    "Prepared for review"
                )


            return {
                "success":
                    True,

                "status":
                    status,

                "dead_job":
                    False,

                "current_url":
                    page.url,

                "application_scope_url":
                    scope_result[
                        "scope_url"
                    ],

                "application_in_iframe":
                    scope_result[
                        "is_frame"
                    ],

                "new_tab_opened":
                    application_result[
                        "new_tab"
                    ],

                "captcha_detected":
                    captcha,

                "hard_blockers":
                    summary_after[
                        "hard_blockers"
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

                "submitted":
                    False,
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
            # leave browser visible
            # for 60 seconds.
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