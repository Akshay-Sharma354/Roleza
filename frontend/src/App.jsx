import { useState } from "react";
import "./App.css";

function App() {
  const [showPreferences, setShowPreferences] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [jobsError, setJobsError] = useState("");

  const [preferences, setPreferences] = useState({
    roleType: "AI",
    location: "India",
    remoteOnly: true,
    resume: "auto",
  });

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setPreferences((current) => ({
      ...current,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setShowPreferences(false);
    setShowResults(true);
    setLoadingJobs(true);
    setJobsError("");

    try {
  const params = new URLSearchParams({
  role_type: preferences.roleType,
  location: preferences.location,
  remote_only: String(preferences.remoteOnly),
});

const response = await fetch(
  `http://127.0.0.1:8000/jobs?${params.toString()}`
);

      if (!response.ok) {
        throw new Error("Unable to load jobs.");
      }

      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (error) {
      setJobsError(
        error instanceof Error ? error.message : "Unable to load jobs."
      );
      setJobs([]);
    } finally {
      setLoadingJobs(false);
    }
  }

  function getSelectedResume() {
    if (preferences.resume === "ai") {
      return "AI Resume";
    }

    if (preferences.resume === "recruitment") {
      return "US IT Resume";
    }

    return preferences.roleType === "US IT Recruiter"
      ? "US IT Resume"
      : "AI Resume";
  }

  return (
    <div className="app">
      <header className="navbar">
        <button
          className="brand brand-button"
          onClick={() => setShowResults(false)}
          aria-label="Return to Roleza home"
        >
          <div className="brand-mark">R</div>
          <span>Roleza</span>
        </button>

        <button
          className="secondary-button"
          onClick={() => setShowPreferences(true)}
        >
          Settings
        </button>
      </header>

      {showResults ? (
        <main className="results-page">
          <div className="results-header">
            <div>
              <p className="eyebrow">MATCHED OPPORTUNITIES</p>
              <h1>Jobs selected for you</h1>

              <p>
                Showing {preferences.roleType} roles for {preferences.location}
                {preferences.remoteOnly
                  ? " with remote-only filtering."
                  : "."}
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={() => setShowPreferences(true)}
            >
              Edit preferences
            </button>
          </div>

          {loadingJobs && (
            <div className="results-message">
              <h2>Searching for matching jobs...</h2>
              <p>Roleza is loading opportunities from the backend.</p>
            </div>
          )}

          {jobsError && (
            <div className="results-message error-message">
              <h2>Could not load jobs</h2>
              <p>{jobsError}</p>
            </div>
          )}

          {!loadingJobs && !jobsError && jobs.length === 0 && (
            <div className="results-message">
              <h2>No matching jobs found</h2>
              <p>Try changing your role or location preferences.</p>
            </div>
          )}

          {!loadingJobs && !jobsError && jobs.length > 0 && (
            <div className="results-grid">
              {jobs.map((job) => (
                <article className="job-card" key={job.id}>
                  <div className="job-card-top">
                    <div>
                      <span className="job-source">{job.source}</span>
                      <h2>{job.title}</h2>
                      <p>{job.company}</p>
                    </div>

                    <span className="fresh-badge">{job.posted}</span>
                  </div>

                  <div className="job-meta">
                    <span>{job.work_mode}</span>
                    <span>{job.location}</span>
                    <span>{job.experience}</span>
                  </div>

                  <p className="job-description">{job.description}</p>

                  <div className="resume-row">
                    <span>
                      {job.requires_human_review
                        ? "Status"
                        : "Resume selected"}
                    </span>

                    <strong>
                      {job.requires_human_review
                        ? job.status
                        : getSelectedResume()}
                    </strong>
                  </div>

                  <div className="job-actions">
                    <button className="secondary-button">
                      Review job
                    </button>

                    <button className="primary-button">
                      Apply
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </main>
      ) : (
        <>
          <main className="hero">
            <section className="hero-copy">
              <p className="eyebrow">AI JOB SEARCH ASSISTANT</p>

              <h1>
                Find the right jobs.
                <br />
                Apply with confidence.
              </h1>

              <p className="hero-description">
                Roleza helps you discover relevant opportunities, choose the
                correct resume, track applications, and identify when human
                action is needed.
              </p>

              <div className="hero-actions">
                <button
                  className="primary-button"
                  onClick={() => setShowPreferences(true)}
                >
                  Start Job Search
                </button>

                <button className="secondary-button">
                  View Applications
                </button>
              </div>
            </section>

            <section className="dashboard-card">
              <div className="card-header">
                <div>
                  <p className="card-label">TODAY&apos;S OVERVIEW</p>
                  <h2>Your job search</h2>
                </div>

                <span className="status-badge">Active</span>
              </div>

              <div className="stats-grid">
                <div className="stat-card">
                  <span>Jobs found</span>
                  <strong>{jobs.length}</strong>
                </div>

                <div className="stat-card">
                  <span>Applications</span>
                  <strong>0</strong>
                </div>

                <div className="stat-card">
                  <span>Needs review</span>
                  <strong>
                    {
                      jobs.filter(
                        (job) => job.requires_human_review
                      ).length
                    }
                  </strong>
                </div>
              </div>

              <div className="activity-box">
                <div className="activity-icon">✓</div>

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
              <span className="feature-number">01</span>
              <h3>Smart matching</h3>
              <p>
                Find roles based on your skills, location, experience, and
                goals.
              </p>
            </article>

            <article>
              <span className="feature-number">02</span>
              <h3>Resume selection</h3>
              <p>
                Automatically use the right resume for AI or recruitment
                roles.
              </p>
            </article>

            <article>
              <span className="feature-number">03</span>
              <h3>Application tracking</h3>
              <p>
                See what was applied to and where your attention is required.
              </p>
            </article>
          </section>
        </>
      )}

      {showPreferences && (
        <div
          className="modal-backdrop"
          onClick={() => setShowPreferences(false)}
        >
          <div
            className="preferences-modal"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <p className="card-label">SEARCH PREFERENCES</p>
                <h2>Find matching jobs</h2>
              </div>

              <button
                className="close-button"
                onClick={() => setShowPreferences(false)}
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
                  <option value="AI">AI Engineer</option>

                  <option value="US IT Recruiter">
                    US IT Recruiter
                  </option>

                  <option value="Both">
                    Both role types
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
                  <option value="India">India</option>

                  <option value="Remote worldwide">
                    Remote worldwide
                  </option>

                  <option value="Singapore">Singapore</option>
                  <option value="Dubai">Dubai</option>
                  <option value="Thailand">Thailand</option>
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

                  <option value="ai">AI resume</option>

                  <option value="recruitment">
                    US IT resume
                  </option>
                </select>
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  name="remoteOnly"
                  checked={preferences.remoteOnly}
                  onChange={handleChange}
                />

                <span>
                  <strong>Remote jobs only</strong>
                  <small>
                    Exclude office and hybrid opportunities.
                  </small>
                </span>
              </label>

              <div className="modal-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowPreferences(false)}
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