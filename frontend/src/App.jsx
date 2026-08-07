import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [currentPage, setCurrentPage] = useState("home");
  const [showPreferences, setShowPreferences] = useState(false);

  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);

  const [loadingJobs, setLoadingJobs] = useState(false);
  const [loadingApplications, setLoadingApplications] = useState(true);

  const [jobsError, setJobsError] = useState("");
  const [applicationsError, setApplicationsError] = useState("");

  const [applyingJobId, setApplyingJobId] = useState(null);

  const [preferences, setPreferences] = useState({
    roleType: "AI",
    location: "India",
    remoteOnly: true,
    resume: "auto",
  });

  useEffect(() => {
    loadApplications();
  }, []);

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setPreferences((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
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
    if (job?.role_type === "US IT Recruiter") {
      return "BDM Resume";
    }

    return "AI Resume";
  }

  function getResumeDownloadUrl(roleType) {
    return `${API_BASE_URL}/resumes/${encodeURIComponent(roleType)}`;
  }

  function isRealJobUrl(jobUrl) {
    if (!jobUrl) {
      return false;
    }

    return !jobUrl.includes("example.com");
  }

  async function loadApplications() {
    setLoadingApplications(true);
    setApplicationsError("");

    try {
      const response = await fetch(`${API_BASE_URL}/applications`);

      if (!response.ok) {
        throw new Error("Unable to load saved applications.");
      }

      const data = await response.json();

      setApplications(data.applications || []);
    } catch (error) {
      setApplicationsError(
        error instanceof Error
          ? error.message
          : "Unable to load saved applications."
      );
    } finally {
      setLoadingApplications(false);
    }
  }

  async function searchJobs() {
    setShowPreferences(false);
    setCurrentPage("results");
    setLoadingJobs(true);
    setJobsError("");

    try {
      const params = new URLSearchParams({
        role_type: preferences.roleType,
        location: preferences.location,
        remote_only: String(preferences.remoteOnly),
      });

      const response = await fetch(
        `${API_BASE_URL}/jobs?${params.toString()}`
      );

      if (!response.ok) {
        throw new Error("Unable to load jobs.");
      }

      const data = await response.json();

      setJobs(data.jobs || []);
    } catch (error) {
      setJobsError(
        error instanceof Error
          ? error.message
          : "Unable to load jobs."
      );

      setJobs([]);
    } finally {
      setLoadingJobs(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await searchJobs();
  }

  async function handleApply(job) {
    if (isJobApplied(job.id) || applyingJobId === job.id) {
      return;
    }

    setApplyingJobId(job.id);
    setApplicationsError("");

    const applicationData = {
      job_id: job.id,
      title: job.title,
      company: job.company,
      role_type: job.role_type,
      location: job.location,
      work_mode: job.work_mode,
      source: job.source,
      resume: job.resume_filename || getResumeLabel(job),
      status: job.requires_human_review
        ? "Needs human review"
        : "Ready to submit",
      requires_human_review: job.requires_human_review,
      job_url: job.job_url || "",
    };

    try {
      const response = await fetch(`${API_BASE_URL}/applications`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(applicationData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to save this application."
        );
      }

      setApplications((current) => [
        data.application,
        ...current,
      ]);
    } catch (error) {
      setApplicationsError(
        error instanceof Error
          ? error.message
          : "Unable to save this application."
      );
    } finally {
      setApplyingJobId(null);
    }
  }

  function isJobApplied(jobId) {
    return applications.some(
      (application) => application.job_id === jobId
    );
  }

  function goHome() {
    setCurrentPage("home");
  }

  async function openApplications() {
    setCurrentPage("applications");
    await loadApplications();
  }

  const humanReviewCount = applications.filter(
    (application) => application.requires_human_review
  ).length;

  return (
    <div className="app">
      <header className="navbar">
        <button
          className="brand brand-button"
          onClick={goHome}
          aria-label="Return to Roleza home"
        >
          <div className="brand-mark">R</div>
          <span>Roleza</span>
        </button>

        <div className="navbar-actions">
          <button
            className="secondary-button"
            onClick={openApplications}
          >
            Applications
          </button>

          <button
            className="secondary-button"
            onClick={() => setShowPreferences(true)}
          >
            Settings
          </button>
        </div>
      </header>

      {currentPage === "home" && (
        <>
          <main className="hero">
            <section className="hero-copy">
              <p className="eyebrow">
                AI JOB SEARCH ASSISTANT
              </p>

              <h1>
                Find the right jobs.
                <br />
                Apply with confidence.
              </h1>

              <p className="hero-description">
                Roleza helps you discover relevant opportunities,
                choose the correct resume, track applications,
                and identify when human action is needed.
              </p>

              <div className="hero-actions">
                <button
                  className="primary-button"
                  onClick={() => setShowPreferences(true)}
                >
                  Start Job Search
                </button>

                <button
                  className="secondary-button"
                  onClick={openApplications}
                >
                  View Applications
                </button>
              </div>
            </section>

            <section className="dashboard-card">
              <div className="card-header">
                <div>
                  <p className="card-label">
                    TODAY&apos;S OVERVIEW
                  </p>

                  <h2>Your job search</h2>
                </div>

                <span className="status-badge">
                  Active
                </span>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <span>Jobs found</span>
                  <strong>{jobs.length}</strong>
                </div>

                <div className="stat-card">
                  <span>Applications</span>
                  <strong>{applications.length}</strong>
                </div>

                <div className="stat-card">
                  <span>Needs review</span>
                  <strong>{humanReviewCount}</strong>
                </div>
              </div>

              <div className="activity-box">
                <div className="activity-icon">
                  ✓
                </div>

                <div>
                  <h3>Roleza is ready</h3>

                  <p>
                    Set your preferences to begin finding matching jobs.
                  </p>
                </div>
              </div>
            </section>
          </main>

          <section className="features">
            <article>
              <span className="feature-number">
                01
              </span>

              <h3>Smart matching</h3>

              <p>
                Find roles based on your skills, location,
                experience, and goals.
              </p>
            </article>

            <article>
              <span className="feature-number">
                02
              </span>

              <h3>Resume selection</h3>

              <p>
                Automatically use the right resume for AI or BDM roles.
              </p>
            </article>

            <article>
              <span className="feature-number">
                03
              </span>

              <h3>Application tracking</h3>

              <p>
                See what was applied to and where your attention
                is required.
              </p>
            </article>
          </section>
        </>
      )}

      {currentPage === "results" && (
        <main className="results-page">
          <div className="results-header">
            <div>
              <p className="eyebrow">
                MATCHED OPPORTUNITIES
              </p>

              <h1>Jobs selected for you</h1>

              <p>
                Showing{" "}
                {getDisplayRoleType(preferences.roleType)}{" "}
                roles for {preferences.location}
                {preferences.remoteOnly
                  ? " with remote-only filtering."
                  : "."}
              </p>
            </div>

            <div className="results-header-actions">
              <button
                className="secondary-button"
                onClick={openApplications}
              >
                View applications
              </button>

              <button
                className="secondary-button"
                onClick={() => setShowPreferences(true)}
              >
                Edit preferences
              </button>
            </div>
          </div>

          {applicationsError && (
            <div className="results-message error-message">
              <h2>Application error</h2>
              <p>{applicationsError}</p>
            </div>
          )}

          {loadingJobs && (
            <div className="results-message">
              <h2>Searching for matching jobs...</h2>

              <p>
                Roleza is loading opportunities from the backend.
              </p>
            </div>
          )}

          {jobsError && (
            <div className="results-message error-message">
              <h2>Could not load jobs</h2>
              <p>{jobsError}</p>

              <button
                className="primary-button retry-button"
                onClick={searchJobs}
              >
                Try again
              </button>
            </div>
          )}

          {!loadingJobs &&
            !jobsError &&
            jobs.length === 0 && (
              <div className="results-message">
                <h2>No matching jobs found</h2>

                <p>
                  Try changing your role or location preferences.
                </p>
              </div>
            )}

          {!loadingJobs &&
            !jobsError &&
            jobs.length > 0 && (
              <div className="results-grid">
                {jobs.map((job) => {
                  const applied = isJobApplied(job.id);
                  const applying =
                    applyingJobId === job.id;

                  return (
                    <article
                      className="job-card"
                      key={job.id}
                    >
                      <div className="job-card-top">
                        <div>
                          <span className="job-source">
                            {job.source}
                          </span>

                          <h2>{job.title}</h2>
                          <p>{job.company}</p>
                        </div>

                        <span className="fresh-badge">
                          {job.posted}
                        </span>
                      </div>

                      <div className="job-meta">
                        <span>{job.work_mode}</span>
                        <span>{job.location}</span>
                        <span>{job.experience}</span>

                        <span>
                          {getDisplayRoleType(
                            job.role_type
                          )}
                        </span>
                      </div>

                      <p className="job-description">
                        {job.description}
                      </p>

                      <div className="resume-row">
                        <span>Resume selected</span>

                        <div>
                          <strong>
                            {job.resume_filename ||
                              getResumeLabel(job)}
                          </strong>

                          <a
                            href={getResumeDownloadUrl(
                              job.role_type
                            )}
                            target="_blank"
                            rel="noreferrer"
                            className="resume-link"
                          >
                            Open resume
                          </a>
                        </div>
                      </div>

                      {!isRealJobUrl(job.job_url) && (
                        <div className="review-warning">
                          <strong>
                            Prototype job
                          </strong>

                          <span>
                            This job currently uses a placeholder URL.
                            Real application URLs will be added when
                            live job sources are connected.
                          </span>
                        </div>
                      )}

                      {job.requires_human_review && (
                        <div className="review-warning">
                          <strong>
                            Human review required
                          </strong>

                          <span>
                            This application may include custom
                            questions, verification, CAPTCHA,
                            login, or another step that needs you.
                          </span>
                        </div>
                      )}

                      <div className="job-actions">
                        <a
                          href={job.job_url}
                          target="_blank"
                          rel="noreferrer"
                          className="secondary-button resume-action-button"
                        >
                          Review job
                        </a>

                        <button
                          className={
                            applied
                              ? "secondary-button applied-button"
                              : "primary-button"
                          }
                          onClick={() => handleApply(job)}
                          disabled={
                            applied || applying
                          }
                        >
                          {applied
                            ? "Added to applications"
                            : applying
                              ? "Saving..."
                              : "Apply"}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            )}
        </main>
      )}

      {currentPage === "applications" && (
        <main className="applications-page">
          <div className="results-header">
            <div>
              <p className="eyebrow">
                APPLICATION TRACKER
              </p>

              <h1>Your applications</h1>

              <p>
                Track jobs, selected resumes,
                and applications requiring your attention.
              </p>
            </div>

            <button
              className="primary-button"
              onClick={() => setShowPreferences(true)}
            >
              Find more jobs
            </button>
          </div>

          {loadingApplications && (
            <div className="results-message">
              <h2>Loading applications...</h2>

              <p>
                Roleza is retrieving your saved application tracker.
              </p>
            </div>
          )}

          {applicationsError && (
            <div className="results-message error-message">
              <h2>Could not load applications</h2>
              <p>{applicationsError}</p>

              <button
                className="primary-button retry-button"
                onClick={loadApplications}
              >
                Try again
              </button>
            </div>
          )}

          {!loadingApplications &&
            !applicationsError &&
            applications.length === 0 && (
              <div className="results-message">
                <h2>No applications yet</h2>

                <p>
                  Search for jobs and press Apply to add
                  opportunities to this tracker.
                </p>

                <button
                  className="primary-button empty-state-button"
                  onClick={() => setShowPreferences(true)}
                >
                  Start job search
                </button>
              </div>
            )}

          {!loadingApplications &&
            !applicationsError &&
            applications.length > 0 && (
              <div className="applications-list">
                {applications.map((application) => (
                  <article
                    className="application-card"
                    key={application.id}
                  >
                    <div className="application-main">
                      <div>
                        <span className="job-source">
                          {application.source}
                        </span>

                        <h2>
                          {application.title}
                        </h2>

                        <p>
                          {application.company}
                        </p>
                      </div>

                      <span
                        className={
                          application.requires_human_review
                            ? "application-status review-status"
                            : "application-status ready-status"
                        }
                      >
                        {application.status}
                      </span>
                    </div>

                    <div className="job-meta">
                      <span>
                        {application.work_mode}
                      </span>

                      <span>
                        {application.location}
                      </span>

                      <span>
                        {getDisplayRoleType(
                          application.role_type
                        )}
                      </span>
                    </div>

                    <div className="application-details">
                      <div>
                        <span>Resume</span>

                        <strong>
                          {application.resume}
                        </strong>

                        <a
                          href={getResumeDownloadUrl(
                            application.role_type
                          )}
                          target="_blank"
                          rel="noreferrer"
                          className="resume-link"
                        >
                          Open resume
                        </a>
                      </div>

                      <div>
                        <span>Added</span>

                        <strong>
                          {new Date(
                            application.applied_at
                          ).toLocaleString()}
                        </strong>
                      </div>
                    </div>

                    {!isRealJobUrl(
                      application.job_url
                    ) && (
                      <div className="review-warning">
                        <strong>
                          Prototype application
                        </strong>

                        <span>
                          This saved application currently
                          points to a placeholder job page.
                        </span>
                      </div>
                    )}

                    <div className="job-actions">
                      <a
                        href={
                          application.job_url || "#"
                        }
                        target="_blank"
                        rel="noreferrer"
                        className="secondary-button resume-action-button"
                      >
                        Review application
                      </a>

                      <a
                        href={
                          application.job_url || "#"
                        }
                        target="_blank"
                        rel="noreferrer"
                        className="primary-button resume-action-button"
                      >
                        Continue application
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            )}
        </main>
      )}

      {showPreferences && (
        <div
          className="modal-backdrop"
          onClick={() =>
            setShowPreferences(false)
          }
        >
          <div
            className="preferences-modal"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-header">
              <div>
                <p className="card-label">
                  SEARCH PREFERENCES
                </p>

                <h2>Find matching jobs</h2>
              </div>

              <button
                className="close-button"
                onClick={() =>
                  setShowPreferences(false)
                }
                aria-label="Close preferences"
              >
                ×
              </button>
            </div>

            <form
              className="preferences-form"
              onSubmit={handleSubmit}
            >
              <label>
                Role type

                <select
                  name="roleType"
                  value={preferences.roleType}
                  onChange={handleChange}
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
                Preferred location

                <select
                  name="location"
                  value={preferences.location}
                  onChange={handleChange}
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
                Resume selection

                <select
                  name="resume"
                  value={preferences.resume}
                  onChange={handleChange}
                >
                  <option value="auto">
                    Choose automatically
                  </option>

                  <option value="ai">
                    AI resume
                  </option>

                  <option value="recruitment">
                    BDM resume
                  </option>
                </select>
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  name="remoteOnly"
                  checked={
                    preferences.remoteOnly
                  }
                  onChange={handleChange}
                />

                <span>
                  <strong>
                    Remote jobs only
                  </strong>

                  <small>
                    Exclude office and hybrid opportunities.
                  </small>
                </span>
              </label>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() =>
                    setShowPreferences(false)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="primary-button"
                >
                  Start Search
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;