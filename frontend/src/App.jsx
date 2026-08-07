import { useState } from "react";
import "./App.css";

function App() {
  const [showPreferences, setShowPreferences] = useState(false);
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

  function handleSubmit(event) {
    event.preventDefault();

    alert(
      `Search started for ${preferences.roleType} roles in ${
        preferences.location
      }. Remote only: ${preferences.remoteOnly ? "Yes" : "No"}`
    );

    setShowPreferences(false);
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <span>Roleza</span>
        </div>

        <button
          className="secondary-button"
          onClick={() => setShowPreferences(true)}
        >
          Settings
        </button>
      </header>

      <main className="hero">
        <section className="hero-copy">
          <p className="eyebrow">AI JOB SEARCH ASSISTANT</p>

          <h1>
            Find the right jobs.
            <br />
            Apply with confidence.
          </h1>

          <p className="hero-description">
            Roleza helps you discover relevant opportunities, choose the correct
            resume, track applications, and identify when human action is needed.
          </p>

          <div className="hero-actions">
            <button
              className="primary-button"
              onClick={() => setShowPreferences(true)}
            >
              Start Job Search
            </button>

            <button className="secondary-button">View Applications</button>
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
              <strong>0</strong>
            </div>

            <div className="stat-card">
              <span>Applications</span>
              <strong>0</strong>
            </div>

            <div className="stat-card">
              <span>Needs review</span>
              <strong>0</strong>
            </div>
          </div>

          <div className="activity-box">
            <div className="activity-icon">✓</div>

            <div>
              <h3>Roleza is ready</h3>
              <p>Set your preferences to begin finding matching jobs.</p>
            </div>
          </div>
        </section>
      </main>

      <section className="features">
        <article>
          <span className="feature-number">01</span>
          <h3>Smart matching</h3>
          <p>Find roles based on your skills, location, experience, and goals.</p>
        </article>

        <article>
          <span className="feature-number">02</span>
          <h3>Resume selection</h3>
          <p>Automatically use the right resume for AI or recruitment roles.</p>
        </article>

        <article>
          <span className="feature-number">03</span>
          <h3>Application tracking</h3>
          <p>See what was applied to and where your attention is required.</p>
        </article>
      </section>

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

            <form className="preferences-form" onSubmit={handleSubmit}>
              <label>
                Role type
                <select
                  name="roleType"
                  value={preferences.roleType}
                  onChange={handleChange}
                >
                  <option value="AI">AI Engineer</option>
                  <option value="US IT Recruiter">US IT Recruiter</option>
                  <option value="Both">Both role types</option>
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
                  <option value="Remote worldwide">Remote worldwide</option>
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
                  <option value="auto">Choose automatically</option>
                  <option value="ai">AI resume</option>
                  <option value="recruitment">US IT resume</option>
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
                  <small>Exclude office and hybrid opportunities.</small>
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

                <button type="submit" className="primary-button">
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