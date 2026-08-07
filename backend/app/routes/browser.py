from pathlib import Path
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from playwright.async_api import (
    async_playwright,
    Page,
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


# =========================================================
# SAFE PROFILE FIELDS
# =========================================================

SAFE_FIELD_KEYWORDS = [
    "first name",
    "firstname",
    "given name",
    "last name",
    "lastname",
    "surname",
    "family name",
    "full name",
    "email",
    "phone",
    "telephone",
    "mobile",
    "resume",
    "cv",
    "curriculum vitae",
    "country off country",
    "country in which you are located",
]


# =========================================================
# QUESTIONS ROLEZA CAN DRAFT
# =========================================================

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


# =========================================================
# QUESTIONS USER MUST ANSWER
# =========================================================

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


# =========================================================
# CONSENT
# =========================================================

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


# =========================================================
# PERSONAL / DEMOGRAPHIC
# =========================================================

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


# =========================================================
# CAPTCHA / LOGIN
# =========================================================

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


APPLY_BUTTON_TEXT = [
    "apply now",
    "apply for this job",
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
    country: str = "India"


# =========================================================
# HELPERS
# =========================================================

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


# =========================================================
# PAGE DETECTION
# =========================================================

async def page_has_text(
    page: Page,
    keywords,
):
    try:
        body_text = normalize(
            await page.locator(
                "body"
            ).inner_text()
        )

    except Exception:
        return False

    return contains_any(
        body_text,
        keywords,
    )


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
            count = (
                await page.locator(
                    selector
                ).count()
            )

            if count > 0:
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
        password_count = (
            await page.locator(
                'input[type="password"]'
            ).count()
        )

        if password_count > 0:
            return True

    except Exception:
        pass

    return await page_has_text(
        page,
        LOGIN_KEYWORDS,
    )


# =========================================================
# OPEN APPLICATION FORM
# =========================================================

async def try_open_application_form(
    page: Page,
):
    for text in APPLY_BUTTON_TEXT:
        pattern = re.compile(
            rf"^{re.escape(text)}$",
            re.IGNORECASE,
        )

        try:
            button = page.get_by_role(
                "button",
                name=pattern,
            )

            if (
                await button.count()
                > 0
            ):
                await button.first.click()

                await page.wait_for_timeout(
                    1500
                )

                return True

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
                await link.first.click()

                await page.wait_for_timeout(
                    1500
                )

                return True

        except Exception:
            pass

    return False


# =========================================================
# FIELD CONTEXT
# =========================================================

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
                label_text = (
                    await label.first.inner_text()
                )

                if label_text:
                    parts.append(
                        label_text
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

    if "*" in context:
        return True

    if "required" in context:
        return True

    return False


# =========================================================
# FIELD CLASSIFIER
# =========================================================

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
# INSPECT FIELDS
# =========================================================

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
                    "index":
                        index,

                    "type":
                        field_type,

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
        category = field.get(
            "category"
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

    can_prepare_application = (
        not captcha
        and not login_wall
    )

    can_submit_automatically = (
        not hard_blockers
        and not user_decisions
        and not personal_questions
        and not draftable_questions
        and not unknown_required
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
            can_prepare_application,

        "can_submit_automatically":
            can_submit_automatically,
    }


# =========================================================
# SAFE AUTOFILL
# =========================================================

async def safe_fill(
    page: Page,
    request: StartApplicationRequest,
):
    filled = []
    skipped = []

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
            input_type = normalize(
                await element.get_attribute(
                    "type"
                )
                or ""
            )

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

            if category != "safe":
                continue

            value = None
            field_name = None

            if any(
                phrase in context
                for phrase in [
                    "first name",
                    "firstname",
                    "given name",
                ]
            ):
                value = request.first_name
                field_name = "First name"

            elif any(
                phrase in context
                for phrase in [
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
                value = request.full_name

                if not value:
                    value = (
                        f"{request.first_name} "
                        f"{request.last_name}"
                    ).strip()

                field_name = "Full name"

            elif "email" in context:
                value = request.email
                field_name = "Email"

            elif any(
                phrase in context
                for phrase in [
                    "phone",
                    "telephone",
                    "mobile",
                ]
            ):
                value = request.phone
                field_name = "Phone"

            elif (
                "country off country"
                in context
                or
                "country in which you are located"
                in context
            ):
                value = request.country
                field_name = "Country"

            if not value:
                continue

            if (
                tag_name == "select"
            ):
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

            if input_type in [
                "hidden",
                "submit",
                "button",
                "checkbox",
                "radio",
                "file",
            ]:
                continue

            try:
                await element.fill(
                    value
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


# =========================================================
# RESUME UPLOAD
# =========================================================

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
            "uploaded":
                False,

            "reason":
                (
                    "Configured resume "
                    "could not be found."
                ),
        }

    file_inputs = (
        page.locator(
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

    for index in range(
        count
    ):
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

    return {
        "uploaded":
            False,

        "reason":
            (
                "Multiple upload fields "
                "detected and Roleza could "
                "not safely identify the "
                "resume field."
            ),
    }


# =========================================================
# TEST
# =========================================================

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
            wait_until=(
                "domcontentloaded"
            ),
            timeout=30000,
        )

        title = (
            await page.title()
        )

        await browser.close()

    return {
        "success": True,
        "title": title,
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

        page = (
            await browser.new_page()
        )

        try:
            await page.goto(
                request.job_url,
                wait_until=(
                    "domcontentloaded"
                ),
                timeout=45000,
            )

            await page.wait_for_timeout(
                1500
            )

            original_url = (
                page.url
            )

            opened_form = (
                await try_open_application_form(
                    page
                )
            )

            await page.wait_for_timeout(
                1200
            )

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
                recommended_action = (
                    "Human action required"
                )

            elif summary[
                "user_decisions"
            ]:
                recommended_action = (
                    "User answers required"
                )

            elif summary[
                "unknown_required_fields"
            ]:
                recommended_action = (
                    "Review unknown required fields"
                )

            elif summary[
                "draftable_questions"
            ]:
                recommended_action = (
                    "Roleza can draft answers for review"
                )

            else:
                recommended_action = (
                    "Safe to prepare application"
                )

            return {
                "success":
                    True,

                "original_url":
                    original_url,

                "current_url":
                    page.url,

                "application_form_opened":
                    opened_form,

                "captcha_detected":
                    captcha,

                "login_detected":
                    login_wall,

                "fields_detected":
                    len(fields),

                "summary":
                    summary,

                "recommended_action":
                    recommended_action,
            }

        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=str(error),
            )

        finally:
            await browser.close()


# =========================================================
# START APPLICATION
# =========================================================

@router.post(
    "/start-application"
)
async def start_application(
    request: StartApplicationRequest,
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
                headless=False
            )
        )

        page = (
            await browser.new_page()
        )

        try:
            await page.goto(
                request.job_url,
                wait_until=(
                    "domcontentloaded"
                ),
                timeout=45000,
            )

            await page.wait_for_timeout(
                1500
            )

            await try_open_application_form(
                page
            )

            await page.wait_for_timeout(
                1200
            )

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
                    "success":
                        False,

                    "status":
                        "Needs human action",

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
                "success":
                    True,

                "status":
                    "Prepared for review",

                "current_url":
                    page.url,

                "filled_fields":
                    fill_result[
                        "filled"
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
            await page.wait_for_timeout(
                5000
            )

            await browser.close()