import { useEffect, useRef } from "react";

const FootballPitch = ({ inputSequence, selectedResult, isLoading }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    ctx.scale(2, 2);

    const width = rect.width;
    const height = rect.height;
    const padding = 20;
    const pitchWidth = width - padding * 2;
    const pitchHeight = height - padding * 2;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Draw pitch background
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, "#1a472a");
    gradient.addColorStop(0.5, "#2d5a3d");
    gradient.addColorStop(1, "#1a472a");
    ctx.fillStyle = gradient;
    ctx.fillRect(padding, padding, pitchWidth, pitchHeight);

    // Draw pitch markings
    ctx.strokeStyle = "rgba(255, 255, 255, 0.6)";
    ctx.lineWidth = 2;

    // Outer boundary
    ctx.strokeRect(padding, padding, pitchWidth, pitchHeight);

    // Center line
    ctx.beginPath();
    ctx.moveTo(width / 2, padding);
    ctx.lineTo(width / 2, height - padding);
    ctx.stroke();

    // Center circle
    const centerX = width / 2;
    const centerY = height / 2;
    const circleRadius = Math.min(pitchWidth, pitchHeight) * 0.12;
    ctx.beginPath();
    ctx.arc(centerX, centerY, circleRadius, 0, Math.PI * 2);
    ctx.stroke();

    // Center dot
    ctx.beginPath();
    ctx.arc(centerX, centerY, 3, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
    ctx.fill();

    // Penalty boxes (18-yard)
    const penaltyWidth = pitchWidth * 0.16;
    const penaltyHeight = pitchHeight * 0.4;
    const penaltyY = height / 2 - penaltyHeight / 2;

    // Left penalty box
    ctx.strokeRect(padding, penaltyY, penaltyWidth, penaltyHeight);

    // Right penalty box
    ctx.strokeRect(width - padding - penaltyWidth, penaltyY, penaltyWidth, penaltyHeight);

    // Goal areas (6-yard) - "Two 6-yard rectangles"
    const goalAreaWidth = penaltyWidth * 0.35; // Approx for 6-yard vs 18-yard
    const goalAreaHeight = penaltyHeight * 0.45;
    const goalAreaY = height / 2 - goalAreaHeight / 2;

    ctx.strokeRect(padding, goalAreaY, goalAreaWidth, goalAreaHeight);
    ctx.strokeRect(width - padding - goalAreaWidth, goalAreaY, goalAreaWidth, goalAreaHeight);

    // Penalty Arcs (The "D")
    // Left Arc
    ctx.beginPath();
    ctx.arc(padding + penaltyWidth, height / 2, circleRadius, -Math.PI / 3, Math.PI / 3);
    ctx.stroke();

    // Right Arc
    ctx.beginPath();
    ctx.arc(width - padding - penaltyWidth, height / 2, circleRadius, Math.PI * 2 / 3, Math.PI * 4 / 3);
    ctx.stroke();

    // Goals - "Two thick lines representing the goal"
    const goalMouthHeight = goalAreaHeight * 0.6; // Width of the actual goal
    const goalMouthY = height / 2 - goalMouthHeight / 2;

    ctx.lineWidth = 5; // Thicker line
    ctx.beginPath();
    // Left Goal
    ctx.moveTo(padding, goalMouthY);
    ctx.lineTo(padding, goalMouthY + goalMouthHeight);
    // Right Goal
    ctx.moveTo(width - padding, goalMouthY);
    ctx.lineTo(width - padding, goalMouthY + goalMouthHeight);
    ctx.stroke();
    ctx.lineWidth = 2; // Reset mark

    // Metric dimensions based on visualizer.py
    const REAL_LENGTH = 105;
    const REAL_WIDTH = 68;

    // Convert coordinates to canvas position
    // Backend uses meters centered at (0,0). X: [-52.5, 52.5], Y: [-34, 34]
    // Canvas X: 0 to pitchWidth
    // Canvas Y: 0 to pitchHeight (Y inverted: +Y is Up in data, Down in canvas)

    const toCanvasX = (x) => {
      const pct = (x + REAL_LENGTH / 2) / REAL_LENGTH;
      return padding + pct * pitchWidth;
    };

    const toCanvasY = (y) => {
      // Invert Y: Top of pitch (positive y) -> Top of canvas (0)
      const pct = (REAL_WIDTH / 2 - y) / REAL_WIDTH;
      return padding + pct * pitchHeight;
    };

    // Draw trajectories
    const drawTrajectory = (coords, color, label) => {
      if (coords.length < 2) return;

      // Draw line
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      ctx.moveTo(toCanvasX(coords[0].x), toCanvasY(coords[0].y));
      for (let i = 1; i < coords.length; i++) {
        ctx.lineTo(toCanvasX(coords[i].x), toCanvasY(coords[i].y));
      }
      ctx.stroke();

      // Draw points
      coords.forEach((coord, index) => {
        const x = toCanvasX(coord.x);
        const y = toCanvasY(coord.y);

        // Outer glow
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.fillStyle = color.replace("1)", "0.3)");
        ctx.fill();

        // Inner circle
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();

        // Number
        ctx.fillStyle = "white";
        ctx.font = "bold 8px Inter";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText((index + 1).toString(), x, y);
      });
    };

    // Draw input sequence (blue)
    if (inputSequence && inputSequence.length > 0) {
      drawTrajectory(inputSequence, "rgba(14, 165, 233, 1)", "Input");
    }

    // Draw selected result sequence (red/orange)
    if (selectedResult?.matchCoordinates) {
      drawTrajectory(
        selectedResult.matchCoordinates,
        "rgba(249, 115, 22, 1)",
        "Match",
      );
    }
  }, [inputSequence, selectedResult]);

  return (
    <div className="card glass-card h-100">
      <div className="card-header">
        <h5 className="card-title mb-2">2D Pitch Visualization</h5>
        <div className="d-flex align-items-center gap-4">
          <div className="d-flex align-items-center gap-2">
            <div
              className="rounded-circle bg-primary"
              style={{ width: "16px", height: "16px" }}
            />
            <span className="text-muted">Input Sequence</span>
          </div>
          <div className="d-flex align-items-center gap-2">
            <div
              className="rounded-circle bg-warning"
              style={{ width: "16px", height: "16px" }}
            />
            <span className="text-muted">Matched Sequence</span>
          </div>
        </div>
      </div>
      <div className="card-body p-0">
        <div
          className="position-relative w-100"
          style={{ aspectRatio: "16/10" }}
        >
          <canvas
            ref={canvasRef}
            className="w-100 h-100"
            style={{ backgroundColor: "#1a472a" }}
          />
          {isLoading && (
            <div className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-dark bg-opacity-50" style={{ zIndex: 10 }}>
              <div className="spinner-border text-light" role="status" style={{ width: '3rem', height: '3rem' }}>
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
          {!inputSequence && !selectedResult && !isLoading && (
            <div className="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-dark bg-opacity-20">
              <p className="text-white text-opacity-70 mb-0">
                Search for sequences to visualize trajectories
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FootballPitch;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }
`}</style>;
