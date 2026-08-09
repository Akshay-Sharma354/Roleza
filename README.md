# Roleza

Roleza is an AI-powered job search and application assistant built to reduce the repetitive work involved in finding and applying to jobs.

It is designed to help users discover relevant roles, evaluate job fit, inspect real application forms, prepare safe application fields, select the correct resume, detect blockers, and involve the user only when human input is actually required.

The long-term goal is simple:

> Find the right jobs, apply faster, and only involve the user when a real decision or human verification is required.

---

## What Roleza Does

Roleza currently supports a semi-automated job application workflow.

It can:

- Discover jobs from multiple sources
- Filter outdated listings
- Detect dead or expired jobs
- Score job fit
- Check remote eligibility
- Follow real employer application links
- Handle ATS redirects, popups, and new tabs
- Detect application forms inside iframes
- Inspect application fields
- Classify application questions
- Fill safe profile information
- Select the appropriate resume
- Detect CAPTCHA and login blockers
- Stop before sensitive or decision-based questions
- Track application activity

---

## Core Goal

Roleza is being built toward this workflow:

```text
Search jobs
→ Check fit
→ Check remote eligibility
→ Verify job is live
→ Open real ATS application
→ Inspect the form
→ Fill safe fields
→ Upload correct resume
→ Answer safe factual questions
→ Pause for CAPTCHA or user decisions
→ Submit when safe
→ Track application
```

Roleza is intentionally designed not to blindly submit applications.

The goal is to automate repetitive work while avoiding fabricated answers, unsafe assumptions, or CAPTCHA bypassing.

---

# Current Features

## Job Discovery

Roleza currently searches jobs from sources including:

- Arbeitnow
- Remote OK
- Greenhouse job boards
- Selected company career pages

Additional ATS providers and job sources can be added over time.

---

## Fresh Job Filtering

Roleza uses a hard freshness rule.

Jobs older than **30 days** are excluded from active search results.

This helps prevent wasting time on outdated opportunities.

---

## Remote Eligibility Detection

Roleza does not assume that every job marked "Remote" is globally remote.

It distinguishes between different remote eligibility types.

Current categories include:

```text
India
Worldwide
US only
EU/UK only
EMEA
Unknown
```

The intended behavior is:

```text
Remote India                         ✅
Worldwide / Global Remote           ✅
International role allowing India   ✅

US-only                              ❌
UK/EU-only                           ❌
EMEA-only                            ❌
Remote eligibility unclear          ⚠ Review
```

The main target is:

> Remote jobs in India and international remote jobs that are genuinely open to candidates based in India.

---

# Job Fit Scoring

Roleza scores jobs using factors such as:

- Role relevance
- Skills match
- Remote eligibility
- Location compatibility
- Job freshness
- Experience alignment
- Restrictions

Job cards can include:

- Fit score
- Priority
- Matched skills
- Fit reasons
- Freshness
- Remote eligibility
- Recommended application action

Possible recommendations include:

```text
Strong candidate for auto-apply
Review
Do not auto-apply
```

---

# Resume Selection

Roleza supports multiple resumes and chooses the appropriate resume based on the job type.

Current setup:

```text
AI roles
→ AI resume

BDM / US IT Recruiter roles
→ BDM resume
```

Resume files are stored locally and are excluded from GitHub.

---

# Browser Automation

Roleza uses Playwright to inspect and prepare real job applications.

It currently supports:

- Direct application links
- Redirects
- New tabs
- Popup windows
- JavaScript-heavy application pages
- Embedded application forms
- Greenhouse iframe applications

Example:

```text
Arbeitnow
→ Apply Now
→ Employer careers page
→ Greenhouse iframe
→ Real application form
```

Roleza can locate the actual application form even when the top-level employer page contains no visible input fields.

---

# Dead Job Detection

Roleza verifies the real employer or ATS destination before preparing an application.

It detects messages such as:

```text
Job not found
Position has been filled
Applications are closed
Job has expired
No longer accepting applications
Page not found
```

Dead jobs can then be removed from active results.

---

# Application Inspection

Before preparing an application, Roleza inspects the actual application form.

Fields are separated into different categories.

---

## Safe Fields

Roleza may automatically fill factual profile information such as:

- First name
- Last name
- Preferred name
- Full name
- Email
- Phone
- Country
- Resume / CV

These are fields that can be populated without making decisions on behalf of the user.

---

## AI-Draftable Questions

Some application questions may eventually be drafted using real resume and project information.

Examples:

- Why are you interested in this role?
- Describe your experience
- Describe a relevant project
- Describe your AI workflow experience
- Describe production AI experience
- Explain your technical background
- Describe customer-facing technical work

Any generated answer should be grounded in real user experience.

Roleza should never fabricate work history or skills.

---

## User Decision Questions

Roleza does not automatically guess answers to decision-sensitive questions such as:

- Work authorization
- Visa sponsorship
- Salary expectations
- Notice period
- Relocation
- Travel availability
- Security clearance
- Citizenship
- Employment restrictions
- Non-compete restrictions
- Skill self-ratings
- Previous employer relationships
- Privacy consent
- Legal acknowledgements

These require explicit user input.

---

## Personal / Demographic Questions

Roleza does not automatically answer sensitive self-identification questions.

Examples:

- Race
- Ethnicity
- Gender
- Sexual orientation
- Disability
- Veteran status
- Pronouns
- Other demographic information

These are intentionally left to the user.

---

# CAPTCHA Handling

Roleza detects CAPTCHA and human verification systems.

It does not attempt to bypass them.

The intended workflow is:

```text
Roleza opens application
→ Roleza fills safe fields
→ CAPTCHA detected
→ User completes verification
→ Application continues
```

Roleza may prepare safe fields before the CAPTCHA, but CAPTCHA completion remains a human action.

---

# Application Form Intelligence

Roleza can currently detect:

- Normal HTML forms
- Dynamic React-based forms
- ATS fields rendered after page load
- Application forms inside iframes
- Greenhouse embedded job applications
- Hidden file upload inputs
- CAPTCHA frames
- Login/account requirements

This is important because many employer career pages do not expose the application form directly on the main webpage.

---

# Current Status

Roleza is under active development.

Current progress:

```text
Find jobs                         ✅
Multiple job sources              ✅
30-day freshness filter           ✅
Job fit scoring                   ✅
Remote eligibility detection      ✅
Dead job detection                ✅
Real ATS link discovery           ✅
Popup/new-tab handling            ✅
Iframe form detection             ✅
Greenhouse iframe support         ✅
Application field inspection      ✅
Field classification              ✅
Safe profile autofill             ✅
CAPTCHA detection                 ✅
Resume selection                  ✅

Reliable resume upload            🚧
ATS-wide autofill                 🚧
More field classifications        🚧
AI-generated application answers  🚧
Controlled auto-submit            🚧
Human handoff workflow            🚧
Multi-user support                🔜
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- Uvicorn
- Playwright
- SQLite

## Frontend

- React
- Vite
- JavaScript
- CSS

## Browser Automation

- Playwright
- Chromium

---

# Planned Capabilities

Future development includes:

- Better ATS-specific adapters
- More reliable resume uploads
- AI-drafted application answers
- Application status tracking
- Human decision memory
- Notifications
- Controlled auto-submit
- CAPTCHA handoff
- Multi-user accounts
- Resume management
- Application analytics

---

# Project Structure

```text
roleza/
│
├── backend/
│   │
│   ├── app/
│   │   ├── agents/
│   │   ├── models/
│   │   ├── routes/
│   │   │   └── browser.py
│   │   │
│   │   ├── services/
│   │   │   ├── job_sources.py
│   │   │   ├── job_scoring.py
│   │   │   ├── greenhouse.py
│   │   │   └── profile.py
│   │   │
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── resumes/
│   ├── profile.json
│   └── roleza.db
│
├── frontend/
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   └── package.json
│
├── .gitignore
│
└── README.md
```

Private profile information, resumes, databases, virtual environments, environment variables, and local files should not be committed to GitHub.

---

# Running Roleza Locally

## Backend

Open Terminal and run:

```bash
cd ~/roleza/backend

source venv/bin/activate

uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

---

## Frontend

Open another Terminal window:

```bash
cd ~/roleza/frontend

npm install

npm run dev
```

The frontend runs at:

```text
http://localhost:5173
```

Open that URL in your browser.

---

# Application Safety Philosophy

Roleza is not intended to behave like a blind job application bot.

The core rule is:

> Automate facts. Pause on decisions.

Roleza should never invent:

- Work authorization
- Visa status
- Sponsorship requirements
- Salary expectations
- Employment history
- Professional experience
- Demographic information
- Legal consent
- Skill ratings
- Personal preferences

Automation should make applications faster without sacrificing accuracy or user control.

---

# Roadmap

## Phase 1 — Job Discovery

- Multi-source job discovery
- Freshness filtering
- Role classification
- Fit scoring
- Remote eligibility

## Phase 2 — Application Intelligence

- Real ATS detection
- Dead job verification
- Popup handling
- Iframe detection
- Form inspection
- Field classification
- CAPTCHA detection

## Phase 3 — Application Preparation

- Safe autofill
- Resume selection
- Resume upload
- AI-drafted answers
- User decision storage

## Phase 4 — Controlled Auto-Apply

- Safe automatic submission
- Human handoff for blockers
- CAPTCHA continuation
- Application confirmation
- Application tracking

## Phase 5 — Productization

- Multi-user support
- Authentication
- User profiles
- Multiple resumes
- Job preferences
- Notifications
- Application analytics

---

# Why Roleza

Applying to jobs involves a large amount of repetitive work.

Candidates repeatedly have to:

- Search multiple job portals
- Check whether listings are still active
- Determine whether "remote" actually includes their country
- Read similar job descriptions
- Upload the same resume
- Enter the same personal information
- Answer similar application questions
- Deal with different ATS platforms
- Track where they have applied

Roleza is being built to remove as much of that repetitive work as possible.

The user should spend time on decisions that actually matter rather than repeatedly entering the same information into job application forms.

---

# The Vision

The long-term vision for Roleza is a personal AI job agent that can:

> Find relevant opportunities, understand whether they are worth applying to, verify eligibility, prepare the application, handle repetitive work, submit when safe, and involve the user only when human judgment is genuinely required.

---

# Disclaimer

Roleza is an experimental personal automation project under active development.

Job portals, employer career sites, and applicant tracking systems may have their own terms, restrictions, authentication requirements, anti-automation mechanisms, and CAPTCHA protections.

Roleza should only automate workflows where automation is technically and legally appropriate.

It is not designed to bypass CAPTCHA, authentication systems, access controls, or other security mechanisms.

---

# Author

Built by **Akshay Sharma**

GitHub:

```text
https://github.com/Akshay-Sharma354
```

Roleza Repository:

```text
https://github.com/Akshay-Sharma354/Roleza
```

---

# Roleza

**Find better roles. Apply smarter. Spend less time filling forms.**
