import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [showPreferences, setShowPreferences] = useState(false);

  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [jobsError, setJobsError] = useState("");

  const [inspectionJob, setInspectionJob] = useState(null);
  const [inspectionData, setInspectionData] = useState(null);
  const [inspectionLoading, setInspectionLoading] =
    useState(false);
  const [inspectionError, setInspectionError] = useState("");

  const [prepareLoading, setPrepareLoading] = useState(false);
  const [prepareData, setPrepareData] = useState(null);
  const [prepareError, setPrepareError] = useState("");

  const [preferences, setPreferences] = useState({
    roleType: "Both",
    location: "India",
    resume: "auto",
    remoteOnly: true,
  });

  useEffect(() => {
    loadApplications();
  }, []);

  async function loadApplications() {
    try {
      const response = await fetch(
        `${API_BASE_URL}/applications`
      );

      const data = await response.json();

      setApplications(
        data.applications || []
      );
    } catch (error) {
      console.error(
        "Could not load applications:",
        error
      );
    }
  }

  async function findJobs() {
    setLoadingJobs(true);
    setJobsError("");

    try {
      const params = new URLSearchParams({
        role_type: preferences.roleType,
        location: preferences.location,
        remote_only: preferences.remoteOnly,
      });

      const response = await fetch(
        `${API_BASE_URL}/jobs?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error(
          "Could not load jobs."
        );
      }

      const data = await response.json();

      setJobs(data.jobs || []);
      setCurrentPage("results");
    } catch (error) {
      console.error(error);

      setJobsError(
        "Roleza could not load live jobs. Make sure the backend is running."
      );
    } finally {
      setLoadingJobs(false);
    }
  }

  function getDisplayRoleType(roleType) {
    if (roleType === "US IT Recruiter") {
      return "BDM";
    }

    if (roleType === "Both") {
      return "AI and BDM";
    }

    return roleType;
  }

  function getResumeLabel(job) {
    if (
      job.role_type === "US IT Recruiter"
    ) {
      return "BDM Resume";
    }

    return "AI Resume";
  }

  function getResumeDownloadUrl(roleType) {
    return `${API_BASE_URL}/resumes/${encodeURIComponent(
      roleType
    )}`;
  }

  function getEligibilityLabel(job) {
    return (
      job.remote_eligibility
      || "Unknown"
    );
  }

  function getEligibilityClass(job) {
    const eligibility =
      job.remote_eligibility
      || "Unknown";

    if (
      eligibility === "Worldwide"
      || eligibility === "India"
    ) {
      return "eligibility-good";
    }

    if (eligibility === "Unknown") {
      return "eligibility-review";
    }

    return "eligibility-limited";
  }

  function getPriorityClass(priority) {
    if (priority === "High") {
      return "priority-high";
    }

    if (priority === "Medium") {
      return "priority-medium";
    }

    return "priority-low";
  }

  function getScoreClass(score) {
    if (score >= 80) {
      return "fit-high";
    }

    if (score >= 60) {
      return "fit-medium";
    }

    return "fit-low";
  }

  function getRecommendationClass(
    recommendation
  ) {
    if (
      recommendation ===
      "Strong candidate for auto-apply"
    ) {
      return "recommendation-good";
    }

    if (
      recommendation ===
      "Review before applying"
    ) {
      return "recommendation-review";
    }

    return "recommendation-skip";
  }

  async function handleApply(job) {
    const payload = {
      job_id: job.id,
      title: job.title,
      company: job.company,
      role_type: job.role_type,
      location: job.location,
      work_mode: job.work_mode,
      source: job.source,

      resume:
        job.resume_filename
        || getResumeLabel(job),

      status:
        job.requires_human_review
          ? "Needs human review"
          : "Ready to submit",

      requires_human_review:
        job.requires_human_review,

      job_url:
        job.job_url || "",

      remote_eligibility:
        job.remote_eligibility
        || "Unknown",
    };

    try {
      const response = await fetch(
        `${API_BASE_URL}/applications`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify(
            payload
          ),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          alert(
            "This job is already in your application tracker."
          );

          return;
        }

        throw new Error(
          data.detail
          || "Could not save application."
        );
      }

      await loadApplications();

      alert(
        "Job added to your application tracker."
      );
    } catch (error) {
      alert(
        error.message
        || "Could not add application."
      );
    }
  }

  async function inspectApplication(job) {
    if (!job.job_url) {
      alert(
        "This job does not have an application URL."
      );

      return;
    }

    setInspectionJob(job);
    setInspectionData(null);
    setInspectionError("");
    setInspectionLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/browser/inspect-application`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            job_url: job.job_url,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Application inspection failed."
        );
      }

      setInspectionData(data);

      if (data.dead_job) {
        setJobs((previousJobs) =>
          previousJobs.filter(
            (item) => item.id !== job.id
          )
        );
      }
    } catch (error) {
      console.error(error);

      setInspectionError(
        error.message
        || "Roleza could not inspect this application."
      );
    } finally {
      setInspectionLoading(false);
    }
  }

  async function prepareApplication(job) {
    if (!job?.job_url) {
      setPrepareError(
        "This job does not have an application URL."
      );
      return;
    }

    setPrepareLoading(true);
    setPrepareData(null);
    setPrepareError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/browser/start-application`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            job_url: job.job_url,
            role_type: job.role_type || "AI",
          }),
        }
      );

      const data = await response.json();

      setPrepareData(data);

      if (!response.ok) {
        throw new Error(
          data.detail
          || "Roleza could not prepare this application."
        );
      }
    } catch (error) {
      console.error(error);

      setPrepareError(
        error.message
        || "Roleza could not prepare this application."
      );
    } finally {
      setPrepareLoading(false);
    }
  }

  function closeInspection() {
    setInspectionJob(null);
    setInspectionData(null);
    setInspectionError("");
    setInspectionLoading(false);

    setPrepareLoading(false);
    setPrepareData(null);
    setPrepareError("");
  }

  function shortenQuestion(context) {
    if (!context) {
      return "Unknown question";
    }

    let cleaned = context
      .replace(
        /^question_\d+\s+off\s+/i,
        ""
      )
      .replace(
        /^\d+\s+off\s+/i,
        ""
      )
      .replace(/\*+$/, "")
      .trim();

    if (cleaned.length > 180) {
      cleaned =
        `${cleaned.slice(0, 177)}...`;
    }

    return cleaned;
  }

  const appliedJobIds = useMemo(
    () =>
      new Set(
        applications.map(
          (application) =>
            application.job_id
        )
      ),
    [applications]
  );

  const highPriorityCount =
    jobs.filter(
      (job) =>
        job.priority === "High"
    ).length;

  const reviewCount =
    jobs.filter(
      (job) =>
        job.requires_human_review
    ).length;

  const inspectionSummary =
    inspectionData?.summary;

  return (
    <div className="app-shell">
      <header className="topbar">
        <button
          className="brand-button"
          onClick={() =>
            setCurrentPage("home")
          }
        >
          <span className="brand-mark">
            R
          </span>

          <span>Roleza</span>
        </button>

        <nav className="topbar-actions">
          <button
            className="nav-button"
            onClick={() =>
              setCurrentPage(
                "applications"
              )
            }
          >
            Applications
          </button>

          <button
            className="settings-button"
            onClick={() =>
              setShowPreferences(true)
            }
          >
            Settings
          </button>
        </nav>
      </header>

      {currentPage === "home" && (
        <main className="home-page">
          <section className="hero-section">
            <div className="hero-badge">
              Your AI job assistant
            </div>

            <h1>
              Find the right jobs.
              <br />
              Apply with confidence.
            </h1>

            <p>
              Roleza searches live job
              sources, filters for your
              preferences, chooses the
              correct resume and helps
              you focus on the best
              opportunities first.
            </p>

            <div className="hero-actions">
              <button
                className="primary-button"
                onClick={findJobs}
                disabled={loadingJobs}
              >
                {loadingJobs
                  ? "Searching..."
                  : "Find jobs"}
              </button>

              <button
                className="secondary-button"
                onClick={() =>
                  setShowPreferences(true)
                }
              >
                Edit preferences
              </button>
            </div>

            {jobsError && (
              <p className="error-text">
                {jobsError}
              </p>
            )}
          </section>

          <section className="overview-card">
            <div>
              <span className="overview-label">
                Jobs found
              </span>

              <strong>
                {jobs.length}
              </strong>
            </div>

            <div>
              <span className="overview-label">
                Applications
              </span>

              <strong>
                {applications.length}
              </strong>
            </div>

            <div>
              <span className="overview-label">
                Needs review
              </span>

              <strong>
                {reviewCount}
              </strong>
            </div>
          </section>

          <section className="feature-grid">
            <article className="feature-card">
              <span className="feature-icon">
                01
              </span>

              <h3>
                Live job search
              </h3>

              <p>
                Search across
                Arbeitnow, Remote OK,
                Greenhouse and your
                company watchlist.
              </p>
            </article>

            <article className="feature-card">
              <span className="feature-icon">
                02
              </span>

              <h3>
                Smart matching
              </h3>

              <p>
                Roleza scores jobs
                based on role fit,
                location, experience
                and freshness.
              </p>
            </article>

            <article className="feature-card">
              <span className="feature-icon">
                03
              </span>

              <h3>
                Application assistant
              </h3>

              <p>
                Inspect application
                forms, detect blockers
                and identify questions
                that need your input.
              </p>
            </article>
          </section>
        </main>
      )}

      {currentPage === "results" && (
        <main className="results-page">
          <section className="results-header">
            <div>
              <button
                className="back-button"
                onClick={() =>
                  setCurrentPage("home")
                }
              >
                ← Back
              </button>

              <h1>
                Recommended jobs
              </h1>

              <p>
                {jobs.length} eligible
                jobs found ·{" "}
                {highPriorityCount} high
                priority
              </p>
            </div>

            <button
              className="primary-button"
              onClick={findJobs}
              disabled={loadingJobs}
            >
              {loadingJobs
                ? "Refreshing..."
                : "Refresh jobs"}
            </button>
          </section>

          {jobs.length === 0 && (
            <section className="empty-state">
              <h2>
                No strong matches
                right now
              </h2>

              <p>
                Roleza did not find
                an eligible job for
                your current
                preferences.
              </p>

              <button
                className="secondary-button"
                onClick={() =>
                  setShowPreferences(true)
                }
              >
                Change preferences
              </button>
            </section>
          )}

          <section className="jobs-list">
            {jobs.map((job) => {
              const alreadyApplied =
                appliedJobIds.has(
                  job.id
                );

              return (
                <article
                  className="job-card"
                  key={job.id}
                >
                  <div className="job-top-row">
                    <div>
                      <span className="source-badge">
                        {job.source}
                      </span>

                      <h2>
                        {job.title}
                      </h2>

                      <p className="company-name">
                        {job.company}
                      </p>
                    </div>

                    <div className="job-score-panel">
                      <div
                        className={`fit-score ${getScoreClass(
                          job.fit_score
                        )}`}
                      >
                        <strong>
                          {job.fit_score ?? 0}%
                        </strong>

                        <span>
                          Fit
                        </span>
                      </div>

                      <span
                        className={`priority-badge ${getPriorityClass(
                          job.priority
                        )}`}
                      >
                        {job.priority || "Low"}{" "}
                        priority
                      </span>
                    </div>
                  </div>

                  <div className="job-meta">
                    <span>
                      📍 {job.location}
                    </span>

                    <span>
                      💻 {job.work_mode}
                    </span>

                    <span>
                      🧭{" "}
                      {getDisplayRoleType(
                        job.role_type
                      )}
                    </span>

                    <span>
                      🕒{" "}
                      {job.freshness
                        || job.posted}
                    </span>
                  </div>

                  <div
                    className={`eligibility-box ${getEligibilityClass(
                      job
                    )}`}
                  >
                    <span>
                      Remote eligibility
                    </span>

                    <strong>
                      {getEligibilityLabel(
                        job
                      )}
                    </strong>
                  </div>

                  {job.application_recommendation && (
                    <div
                      className={`recommendation-box ${getRecommendationClass(
                        job.application_recommendation
                      )}`}
                    >
                      <span>
                        Roleza recommendation
                      </span>

                      <strong>
                        {
                          job.application_recommendation
                        }
                      </strong>
                    </div>
                  )}

                  {job.matched_skills &&
                    job.matched_skills.length > 0 && (
                      <div className="matched-skills-section">
                        <span className="match-title">
                          Matched skills
                        </span>

                        <div className="reason-tags">
                          {job.matched_skills.map(
                            (skill) => (
                              <span
                                className="skill-tag"
                                key={`${job.id}-${skill}`}
                              >
                                {skill}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}

                  {job.fit_reasons &&
                    job.fit_reasons.length > 0 && (
                      <div className="match-reasons">
                        <span className="match-title">
                          Why Roleza scored this job
                        </span>

                        <div className="reason-tags">
                          {job.fit_reasons.map(
                            (
                              reason,
                              index
                            ) => (
                              <span
                                className="reason-tag"
                                key={`${job.id}-${index}`}
                              >
                                {reason}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}

                  <p className="job-description">
                    {job.description}
                  </p>

                  <div className="resume-row">
                    <div>
                      <span>
                        Resume:
                      </span>

                      <strong>
                        {job.resume_filename
                          || getResumeLabel(job)}
                      </strong>

                      <a
                        className="resume-link"
                        href={getResumeDownloadUrl(
                          job.role_type
                        )}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open resume
                      </a>
                    </div>
                  </div>

                  {job.requires_human_review && (
                    <div className="review-warning">
                      ⚠ Remote eligibility
                      or application
                      requirements need
                      human review.
                    </div>
                  )}

                  <div className="job-actions">
                    {job.job_url && (
                      <a
                        className="secondary-button resume-action-button"
                        href={job.job_url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Review job
                      </a>
                    )}

                    {job.job_url && (
                      <button
                        className="inspect-button"
                        onClick={() =>
                          inspectApplication(
                            job
                          )
                        }
                      >
                        Inspect application
                      </button>
                    )}

                    <button
                      className="primary-button"
                      disabled={alreadyApplied}
                      onClick={() =>
                        handleApply(job)
                      }
                    >
                      {alreadyApplied
                        ? "In tracker"
                        : "Add to tracker"}
                    </button>
                  </div>
                </article>
              );
            })}
          </section>
        </main>
      )}

      {currentPage === "applications" && (
        <main className="applications-page">
          <section className="results-header">
            <div>
              <button
                className="back-button"
                onClick={() =>
                  setCurrentPage("home")
                }
              >
                ← Back
              </button>

              <h1>
                Applications
              </h1>

              <p>
                {applications.length} jobs
                in your tracker
              </p>
            </div>

            <button
              className="primary-button"
              onClick={findJobs}
            >
              Find more jobs
            </button>
          </section>

          {applications.length === 0 && (
            <section className="empty-state">
              <h2>
                No applications yet
              </h2>

              <p>
                Jobs you choose from
                Roleza will appear here.
              </p>
            </section>
          )}

          <section className="applications-list">
            {applications.map(
              (application) => (
                <article
                  className="application-card"
                  key={application.id}
                >
                  <div>
                    <span className="source-badge">
                      {application.source}
                    </span>

                    <h2>
                      {application.title}
                    </h2>

                    <p className="company-name">
                      {application.company}
                    </p>
                  </div>

                  <div className="job-meta">
                    <span>
                      📍{" "}
                      {application.location}
                    </span>

                    <span>
                      🧭{" "}
                      {getDisplayRoleType(
                        application.role_type
                      )}
                    </span>

                    <span>
                      🌍{" "}
                      {
                        application.remote_eligibility
                      }
                    </span>
                  </div>

                  <div className="resume-row">
                    <div>
                      <span>
                        Resume:
                      </span>

                      <strong>
                        {
                          application.resume
                        }
                      </strong>

                      <a
                        className="resume-link"
                        href={getResumeDownloadUrl(
                          application.role_type
                        )}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open resume
                      </a>
                    </div>
                  </div>

                  <div className="application-status-row">
                    <span>
                      Status
                    </span>

                    <strong>
                      {application.status}
                    </strong>
                  </div>

                  <p className="application-date">
                    Added:{" "}
                    {
                      application.applied_at
                    }
                  </p>

                  {application.job_url && (
                    <div className="job-actions">
                      <a
                        className="secondary-button resume-action-button"
                        href={
                          application.job_url
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        Review application
                      </a>

                      <button
                        className="inspect-button"
                        onClick={() =>
                          inspectApplication({
                            ...application,
                            job_url:
                              application.job_url,
                          })
                        }
                      >
                        Inspect application
                      </button>
                    </div>
                  )}
                </article>
              )
            )}
          </section>
        </main>
      )}

      {showPreferences && (
        <div className="modal-overlay">
          <div className="preferences-modal">
            <div className="modal-header">
              <div>
                <h2>
                  Job preferences
                </h2>

                <p>
                  Tell Roleza what
                  opportunities to
                  prioritize.
                </p>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setShowPreferences(false)
                }
              >
                ×
              </button>
            </div>

            <label>
              Role type

              <select
                value={
                  preferences.roleType
                }
                onChange={(event) =>
                  setPreferences(
                    (previous) => ({
                      ...previous,
                      roleType:
                        event.target.value,
                    })
                  )
                }
              >
                <option value="AI">
                  AI Engineer
                </option>

                <option value="US IT Recruiter">
                  BDM Roles
                </option>

                <option value="Both">
                  AI and BDM Roles
                </option>
              </select>
            </label>

            <label>
              Location

              <select
                value={
                  preferences.location
                }
                onChange={(event) =>
                  setPreferences(
                    (previous) => ({
                      ...previous,
                      location:
                        event.target.value,
                    })
                  )
                }
              >
                <option value="India">
                  India
                </option>

                <option value="Remote worldwide">
                  Remote worldwide
                </option>

                <option value="Singapore">
                  Singapore
                </option>

                <option value="Dubai">
                  Dubai
                </option>

                <option value="Thailand">
                  Thailand
                </option>
              </select>
            </label>

            <label>
              Resume preference

              <select
                value={
                  preferences.resume
                }
                onChange={(event) =>
                  setPreferences(
                    (previous) => ({
                      ...previous,
                      resume:
                        event.target.value,
                    })
                  )
                }
              >
                <option value="auto">
                  Choose automatically
                </option>

                <option value="ai">
                  AI Resume
                </option>

                <option value="bdm">
                  BDM Resume
                </option>
              </select>
            </label>

            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={
                  preferences.remoteOnly
                }
                onChange={(event) =>
                  setPreferences(
                    (previous) => ({
                      ...previous,
                      remoteOnly:
                        event.target.checked,
                    })
                  )
                }
              />

              Remote jobs only
            </label>

            <div className="modal-actions">
              <button
                className="secondary-button"
                onClick={() =>
                  setShowPreferences(false)
                }
              >
                Cancel
              </button>

              <button
                className="primary-button"
                onClick={() => {
                  setShowPreferences(false);
                  findJobs();
                }}
              >
                Save & find jobs
              </button>
            </div>
          </div>
        </div>
      )}

      {inspectionJob && (
        <div className="modal-overlay">
          <div className="inspection-modal">
            <div className="modal-header">
              <div>
                <span className="inspection-eyebrow">
                  Application inspection
                </span>

                <h2>
                  {inspectionJob.title}
                </h2>

                <p>
                  {inspectionJob.company}
                </p>
              </div>

              <button
                className="close-button"
                onClick={
                  closeInspection
                }
              >
                ×
              </button>
            </div>

            {inspectionLoading && (
              <div className="inspection-loading">
                <div className="inspection-spinner" />

                <h3>
                  Inspecting application…
                </h3>

                <p>
                  Roleza is opening the
                  application page and
                  checking its fields.
                </p>
              </div>
            )}

            {inspectionError && (
              <div className="inspection-error">
                <strong>
                  Inspection failed
                </strong>

                <p>
                  {inspectionError}
                </p>
              </div>
            )}

            {!inspectionLoading &&
              inspectionData?.dead_job && (
                <div className="dead-job-result">
                  <div className="dead-job-icon">
                    ✕
                  </div>

                  <h3>
                    This job is no longer available
                  </h3>

                  <p>
                    Roleza followed the real application
                    link and found that the employer's
                    application page is closed or missing.
                  </p>

                  {inspectionData.dead_job_reason && (
                    <div className="dead-job-reason">
                      Detected:{" "}
                      <strong>
                        {inspectionData.dead_job_reason}
                      </strong>
                    </div>
                  )}

                  <div className="dead-job-actions">
                    <button
                      className="primary-button"
                      onClick={closeInspection}
                    >
                      Remove & continue
                    </button>
                  </div>
                </div>
              )}

            {!inspectionLoading &&
              inspectionSummary && (
                <>
                  <div className="inspection-status">
                    <div>
                      <span>
                        Recommended action
                      </span>

                      <strong>
                        {
                          inspectionData.recommended_action
                        }
                      </strong>
                    </div>

                    <span
                      className={
                        inspectionSummary
                          .hard_blockers
                          .length > 0
                          ? "inspection-status-bad"
                          : "inspection-status-good"
                      }
                    >
                      {
                        inspectionSummary
                          .hard_blockers
                          .length > 0
                          ? "Human action needed"
                          : "Ready to prepare"
                      }
                    </span>
                  </div>

                  <div className="inspection-stats">
                    <div>
                      <strong>
                        {
                          inspectionSummary
                            .counts.total
                        }
                      </strong>

                      <span>
                        Fields
                      </span>
                    </div>

                    <div>
                      <strong>
                        {
                          inspectionSummary
                            .counts.safe
                        }
                      </strong>

                      <span>
                        Safe
                      </span>
                    </div>

                    <div>
                      <strong>
                        {
                          inspectionSummary
                            .counts.draftable
                        }
                      </strong>

                      <span>
                        AI draftable
                      </span>
                    </div>

                    <div>
                      <strong>
                        {
                          inspectionSummary
                            .counts.user_decisions
                        }
                      </strong>

                      <span>
                        Your decisions
                      </span>
                    </div>

                    <div>
                      <strong>
                        {
                          inspectionSummary
                            .counts.personal_questions
                        }
                      </strong>

                      <span>
                        Personal
                      </span>
                    </div>
                  </div>

                  {inspectionSummary
                    .hard_blockers
                    .length > 0 && (
                    <InspectionSection
                      title="Hard blockers"
                      subtitle="Roleza will stop here instead of trying to bypass these."
                      items={
                        inspectionSummary
                          .hard_blockers
                      }
                      type="danger"
                      simple
                    />
                  )}

                  {inspectionSummary
                    .draftable_questions
                    .length > 0 && (
                    <InspectionSection
                      title="AI-draftable questions"
                      subtitle="Roleza can later draft answers from your resume and project history."
                      items={
                        inspectionSummary
                          .draftable_questions
                      }
                      formatItem={
                        shortenQuestion
                      }
                      type="draft"
                    />
                  )}

                  {inspectionSummary
                    .user_decisions
                    .length > 0 && (
                    <InspectionSection
                      title="Needs your decision"
                      subtitle="Roleza will not guess these answers."
                      items={
                        inspectionSummary
                          .user_decisions
                      }
                      formatItem={
                        shortenQuestion
                      }
                      type="warning"
                    />
                  )}

                  {inspectionSummary
                    .personal_questions
                    .length > 0 && (
                    <InspectionSection
                      title="Personal questions"
                      subtitle="Roleza will not guess demographic or personal self-identification answers."
                      items={
                        inspectionSummary
                          .personal_questions
                      }
                      formatItem={
                        shortenQuestion
                      }
                      type="personal"
                    />
                  )}

                  {inspectionSummary
                    .unknown_required_fields
                    .length > 0 && (
                    <InspectionSection
                      title="Unknown required fields"
                      subtitle="These still need classification before Roleza should automate them."
                      items={
                        inspectionSummary
                          .unknown_required_fields
                      }
                      formatItem={
                        shortenQuestion
                      }
                      type="warning"
                    />
                  )}

                  <div className="inspection-actions">
                    <button
                      className="secondary-button"
                      onClick={
                        closeInspection
                      }
                    >
                      Close
                    </button>

                    <a
                      className="secondary-button resume-action-button"
                      href={
                        inspectionJob.job_url
                      }
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open application
                    </a>

                    <button
                      className="primary-button"
                      disabled={
                        !inspectionSummary
                          .can_prepare_application
                        || prepareLoading
                      }
                      title={
                        inspectionSummary
                          .can_prepare_application
                          ? ""
                          : "Resolve the hard blocker before Roleza can prepare this application."
                      }
                      onClick={() =>
                        prepareApplication(
                          inspectionJob
                        )
                      }
                    >
                      {prepareLoading
                        ? "Preparing..."
                        : "Prepare application"}
                    </button>
                  </div>

                  {prepareError && (
                    <div className="prepare-result prepare-result-error">
                      <strong>
                        Preparation failed
                      </strong>

                      <p>
                        {prepareError}
                      </p>
                    </div>
                  )}

                  {prepareData && (
                    <div className="prepare-result">
                      <div className="prepare-result-header">
                        <div>
                          <span>
                            Application preparation
                          </span>

                          <strong>
                            {prepareData.status
                              || "Completed"}
                          </strong>
                        </div>

                        <span
                          className={
                            prepareData.success
                              ? "prepare-success"
                              : "prepare-warning"
                          }
                        >
                          {prepareData.success
                            ? "Prepared"
                            : "Human action needed"}
                        </span>
                      </div>

                      {prepareData.filled_fields &&
                        prepareData.filled_fields.length > 0 && (
                          <div className="prepare-detail">
                            <span>
                              Fields filled
                            </span>

                            <strong>
                              {prepareData.filled_fields.join(
                                ", "
                              )}
                            </strong>
                          </div>
                        )}

                      {prepareData.resume && (
                        <div className="prepare-detail">
                          <span>
                            Resume
                          </span>

                          <strong>
                            {prepareData.resume.uploaded
                              ? `Uploaded: ${prepareData.resume.filename}`
                              : prepareData.resume.reason
                                || "Not uploaded"}
                          </strong>
                        </div>
                      )}

                      {prepareData.hard_blockers &&
                        prepareData.hard_blockers.length > 0 && (
                          <div className="prepare-detail">
                            <span>
                              Blocker
                            </span>

                            <strong>
                              {prepareData.hard_blockers.join(
                                ", "
                              )}
                            </strong>
                          </div>
                        )}

                      <div className="prepare-detail">
                        <span>
                          Submitted
                        </span>

                        <strong>
                          {prepareData.submitted
                            ? "Yes"
                            : "No — waiting for review"}
                        </strong>
                      </div>
                    </div>
                  )}

                  {!inspectionSummary
                    .can_prepare_application && (
                    <p className="inspection-note">
                      Prepare application is
                      disabled because Roleza
                      detected a CAPTCHA or
                      login blocker.
                    </p>
                  )}
                </>
              )}
          </div>
        </div>
      )}
    </div>
  );
}

function InspectionSection({
  title,
  subtitle,
  items,
  formatItem,
  type,
  simple = false,
}) {
  return (
    <section
      className={`inspection-section inspection-${type}`}
    >
      <div className="inspection-section-header">
        <div>
          <h3>
            {title}
          </h3>

          <p>
            {subtitle}
          </p>
        </div>

        <strong>
          {items.length}
        </strong>
      </div>

      <div className="inspection-items">
        {items.map(
          (item, index) => {
            const text = simple
              ? item
              : formatItem
                ? formatItem(
                    item.context
                  )
                : item.context;

            return (
              <div
                className="inspection-item"
                key={`${title}-${index}`}
              >
                <span>
                  {text}
                </span>

                {!simple &&
                  item.required && (
                    <small>
                      Required
                    </small>
                  )}
              </div>
            );
          }
        )}
      </div>
    </section>
  );
}

export default App;