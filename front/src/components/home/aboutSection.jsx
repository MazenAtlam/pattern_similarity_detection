import { AudioWaveform, TrendingUp, Zap, BarChart3 } from "lucide-react";

const AboutSection = () => {
  return (
    <section id="about" className="py-5 bg-light">
      <div className="container">
        <div className="text-center mb-5">
          <h2 className="h1 fw-bold mb-3">How It Works</h2>
          <p className="lead text-muted mx-auto" style={{ maxWidth: "600px" }}>
            Leveraging advanced signal processing techniques to find patterns in
            complex data.
          </p>
        </div>

        <div className="row g-4 justify-content-center">
          {/* Audio Analysis Card */}
          <div className="col-lg-6">
            <div className="card glass-card overflow-hidden h-100">
              <div
                className="bg-gradient"
                style={{
                  height: "8px",
                  background:
                    "linear-gradient(to right, var(--primary), var(--primary-light))",
                }}
              />
              <div className="card-body">
                <div
                  className="rounded-3 bg-primary bg-opacity-10 d-flex align-items-center justify-content-center mb-4"
                  style={{ width: "56px", height: "56px" }}
                >
                  <AudioWaveform
                    style={{
                      width: "28px",
                      height: "28px",
                      color: "var(--primary)",
                    }}
                  />
                </div>
                <h5 className="card-title mb-3">Audio Melody Detection</h5>
                <p className="card-text text-muted mb-4">
                  Our system uses{" "}
                  <strong>Short-Time Fourier Transform (STFT)</strong> to
                  analyze the frequency content of your hummed melody over time.
                </p>
                <div className="d-flex gap-3 p-3 rounded-3 bg-light mb-4">
                  <Zap
                    style={{
                      width: "20px",
                      height: "20px",
                      color: "var(--primary)",
                    }}
                  />
                  <div>
                    <p className="fw-medium mb-1">Key Features</p>
                    <p className="small text-muted mb-0">
                      Pitch extraction, frequency analysis, and pattern matching
                      against our song database.
                    </p>
                  </div>
                </div>
                <div className="d-flex flex-wrap gap-2">
                  {[
                    "STFT",
                    "Pitch Detection",
                    "Spectral Analysis",
                    "Pattern Matching",
                  ].map((tag) => (
                    <span
                      key={tag}
                      className="badge bg-primary bg-opacity-10 text-primary px-3 py-2"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Spatial Analysis Card */}
          <div className="col-lg-6">
            <div className="card glass-card overflow-hidden h-100">
              <div
                className="bg-gradient"
                style={{
                  height: "8px",
                  background:
                    "linear-gradient(to right, var(--accent), var(--accent-light))",
                }}
              />
              <div className="card-body">
                <div
                  className="rounded-3 bg-accent bg-opacity-10 d-flex align-items-center justify-content-center mb-4"
                  style={{ width: "56px", height: "56px" }}
                >
                  <TrendingUp
                    style={{
                      width: "28px",
                      height: "28px",
                      color: "var(--accent)",
                    }}
                  />
                </div>
                <h5 className="card-title mb-3">Spatial Trajectory Analysis</h5>
                <p className="card-text text-muted mb-4">
                  Using <strong>Discrete Fourier Transform (DFT)</strong> to
                  analyze player movement trajectories and identify similar
                  tactical patterns.
                </p>
                <div className="d-flex gap-3 p-3 rounded-3 bg-light mb-4">
                  <BarChart3
                    style={{
                      width: "20px",
                      height: "20px",
                      color: "var(--accent)",
                    }}
                  />
                  <div>
                    <p className="fw-medium mb-1">Key Features</p>
                    <p className="small text-muted mb-0">
                      2D trajectory comparison, pass sequence matching, and
                      tactical similarity scoring.
                    </p>
                  </div>
                </div>
                <div className="d-flex flex-wrap gap-2">
                  {[
                    "DFT",
                    "2D Analysis",
                    "Trajectory Matching",
                    "Tactical Patterns",
                  ].map((tag) => (
                    <span
                      key={tag}
                      className="badge bg-accent bg-opacity-10 text-accent px-3 py-2"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AboutSection;

<style jsx>{`
  :root {
    --primary: #3b82f6;
    --primary-light: #93c5fd;
    --accent: #8b5cf6;
    --accent-light: #c4b5fd;
  }

  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
    transition:
      transform 0.3s,
      box-shadow 0.3s;
  }

  .glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  }
`}</style>;
