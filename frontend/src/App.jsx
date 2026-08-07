import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <span>Roleza</span>
        </div>

        <button className="secondary-button">Settings</button>
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
            <button className="primary-button">Start Job Search</button>
            <button className="secondary-button">View Applications</button>
          </div>
        </section>

        <section className="dashboard-card">
          <div className="card-header">
            <div>
              <p className="card-label">TODAY'S OVERVIEW</p>
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
    </div>
  );
}

export default App;