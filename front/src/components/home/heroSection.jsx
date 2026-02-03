import { Link } from "react-router-dom";
import { Music, Footprints, ArrowRight, Waves } from "lucide-react";

const HeroSection = () => {
  return (
    <section className="position-relative min-vh-90 d-flex align-items-center overflow-hidden">
      {/* Background */}
      <div className="position-absolute top-0 start-0 w-100 h-100 hero-gradient" />

      {/* Floating Elements */}
      <div
        className="position-absolute top-0 start-0 w-25 h-25 rounded-circle bg-primary bg-opacity-10 blur-3 float-animation"
        style={{ top: "20%", left: "10%" }}
      />
      <div
        className="position-absolute bottom-0 end-0 w-50 h-50 rounded-circle bg-accent bg-opacity-10 blur-3 float-animation"
        style={{ animationDelay: "-3s" }}
      />

      <div className="container position-relative z-3">
        <div className="mx-auto text-center" style={{ maxWidth: "900px" }}>
          {/* Badge */}
          <div className="d-inline-flex align-items-center gap-2 px-3 py-2 rounded-pill bg-primary bg-opacity-10 border border-primary border-opacity-20 mb-4 animate-fade-in">
            <Waves
              style={{ width: "16px", height: "16px", color: "var(--primary)" }}
            />
            <span className="fw-medium" style={{ color: "var(--primary)" }}>
              DSP-Powered Analysis
            </span>
          </div>

          {/* Title */}
          <h1
            className="display-3 fw-bold mb-4 animate-fade-in"
            style={{ animationDelay: "0.1s" }}
          >
            Discover Patterns in{" "}
            <span className="gradient-text">Sound and Space</span>
          </h1>

          {/* Subtitle */}
          <p
            className="lead text-muted mb-5 mx-auto animate-fade-in"
            style={{ maxWidth: "600px", animationDelay: "0.2s" }}
          >
            Using Fourier Transforms to detect similarity in musical melodies
            and football tactical sequences.
          </p>

          {/* Action Cards */}
          <div
            className="row g-4 mx-auto animate-fade-in"
            style={{ maxWidth: "800px", animationDelay: "0.3s" }}
          >
            <div className="col-md-6">
              <Link to="/songs" className="text-decoration-none">
                <div className="card glass-card h-100 hover-lift">
                  <div className="card-body text-center p-4">
                    <div
                      className="rounded-3 bg-gradient d-flex align-items-center justify-content-center mx-auto mb-4"
                      style={{
                        width: "64px",
                        height: "64px",
                        background:
                          "linear-gradient(to bottom right, var(--primary), var(--primary-light))",
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                      }}
                    >
                      <Music
                        style={{
                          width: "32px",
                          height: "32px",
                          color: "white",
                        }}
                      />
                    </div>
                    <div className="mb-4">
                      <h3 className="h5 fw-semibold mb-2">Try Song Detector</h3>
                      <p className="text-muted small">
                        Hum a melody and find matching songs
                      </p>
                    </div>
                    <button className="btn btn-gradient w-100">
                      Get Started
                      <ArrowRight
                        style={{ width: "16px", height: "16px" }}
                        className="ms-2"
                      />
                    </button>
                  </div>
                </div>
              </Link>
            </div>

            <div className="col-md-6">
              <Link to="/fifa" className="text-decoration-none">
                <div className="card glass-card h-100 hover-lift">
                  <div className="card-body text-center p-4">
                    <div
                      className="rounded-3 bg-gradient d-flex align-items-center justify-content-center mx-auto mb-4"
                      style={{
                        width: "64px",
                        height: "64px",
                        background:
                          "linear-gradient(to bottom right, var(--accent), var(--accent-light))",
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                      }}
                    >
                      <Footprints
                        style={{
                          width: "32px",
                          height: "32px",
                          color: "white",
                        }}
                      />
                    </div>
                    <div className="mb-4">
                      <h3 className="h5 fw-semibold mb-2">
                        FIFA Sequence Detector
                      </h3>
                      <p className="text-muted small">
                        Analyze World Cup 2022 pass patterns
                      </p>
                    </div>
                    <button className="btn btn-outline-accent w-100">
                      Explore Now
                      <ArrowRight
                        style={{ width: "16px", height: "16px" }}
                        className="ms-2"
                      />
                    </button>
                  </div>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;

<style jsx>{`
  .min-vh-90 {
    min-height: 90vh;
  }

  .hero-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    opacity: 0.05;
  }

  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }

  .hover-lift {
    transition:
      transform 0.3s,
      box-shadow 0.3s;
  }

  .hover-lift:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  }

  .gradient-text {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .btn-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
  }

  .btn-outline-accent {
    border-color: var(--accent);
    color: var(--accent);
  }

  .btn-outline-accent:hover {
    background-color: var(--accent);
    color: white;
  }

  .blur-3 {
    filter: blur(48px);
  }

  @keyframes float {
    0%,
    100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-20px);
    }
  }

  .float-animation {
    animation: float 6s ease-in-out infinite;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fade-in {
    animation: fadeIn 0.6s ease-out forwards;
  }
`}</style>;
