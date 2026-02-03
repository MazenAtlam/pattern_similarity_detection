import { useState } from "react";
import { Search, Upload, Plus, X, Users } from "lucide-react";

const FifaForm = ({ onSearchByMetadata, onUploadSequence, isLoading }) => {
  const [stage, setStage] = useState("");
  const [group, setGroup] = useState("");
  const [date, setDate] = useState("");
  const [match, setMatch] = useState("");
  const [players, setPlayers] = useState([]);
  const [playerInput, setPlayerInput] = useState("");

  const stages = [
    "Group Stage",
    "Round of 16",
    "Quarter-Finals",
    "Semi-Finals",
    "Final",
  ];

  const groups = ["A", "B", "C", "D", "E", "F", "G", "H"];

  const handleAddPlayer = () => {
    if (playerInput.trim() && players.length < 5) {
      setPlayers([...players, playerInput.trim()]);
      setPlayerInput("");
    }
  };

  const handleRemovePlayer = (index) => {
    setPlayers(players.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddPlayer();
    }
  };

  const handleSearch = () => {
    onSearchByMetadata({ stage, group, date, match, players });
  };

  return (
    <div className="card glass-card">
      <div className="card-header">
        <h5 className="card-title mb-0 d-flex align-items-center gap-2">
          <Search
            style={{ width: "20px", height: "20px", color: "var(--primary)" }}
          />
          Search Pass Sequences
        </h5>
      </div>
      <div className="card-body">
        <div className="row g-3 mb-4">
          {/* Stage */}
          <div className="col-md-6 col-lg-3">
            <label className="form-label">Stage</label>
            <select
              className="form-select bg-light"
              value={stage}
              onChange={(e) => setStage(e.target.value)}
            >
              <option value="">Select stage</option>
              {stages.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Group */}
          <div className="col-md-6 col-lg-3">
            <label className="form-label">Group</label>
            <select
              className="form-select bg-light"
              value={group}
              onChange={(e) => setGroup(e.target.value)}
              disabled={stage !== "Group Stage"}
            >
              <option value="">Select group</option>
              {groups.map((g) => (
                <option key={g} value={g}>
                  Group {g}
                </option>
              ))}
            </select>
          </div>

          {/* Date */}
          <div className="col-md-6 col-lg-3">
            <label className="form-label">Date</label>
            <input
              type="date"
              className="form-control bg-light"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min="2022-11-20"
              max="2022-12-18"
            />
          </div>

          {/* Match */}
          <div className="col-md-6 col-lg-3">
            <label className="form-label">Match</label>
            <input
              type="text"
              className="form-control bg-light"
              placeholder="e.g., Argentina vs France"
              value={match}
              onChange={(e) => setMatch(e.target.value)}
            />
          </div>
        </div>

        {/* Players Sequence */}
        <div className="mb-4">
          <label className="form-label d-flex align-items-center gap-2">
            <Users
              style={{ width: "16px", height: "16px" }}
              className="text-muted"
            />
            Players Sequence (Max 5)
          </label>
          <div className="d-flex gap-2 mb-3">
            <input
              type="text"
              className="form-control bg-light"
              placeholder="Enter player name"
              value={playerInput}
              onChange={(e) => setPlayerInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={players.length >= 5}
            />
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={handleAddPlayer}
              disabled={players.length >= 5 || !playerInput.trim()}
            >
              <Plus style={{ width: "16px", height: "16px" }} />
            </button>
          </div>

          {/* Player Badges */}
          {players.length > 0 && (
            <div className="d-flex flex-wrap gap-2 mb-3">
              {players.map((player, index) => (
                <span
                  key={index}
                  className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-20 d-flex align-items-center gap-2 py-2 px-3"
                >
                  <span className="text-muted me-1">{index + 1}.</span>
                  {player}
                  <button
                    onClick={() => handleRemovePlayer(index)}
                    className="btn-close btn-close-sm"
                    style={{ fontSize: "0.75rem" }}
                  />
                </span>
              ))}
            </div>
          )}

          {players.length > 1 && (
            <p className="text-muted small">Sequence: {players.join(" → ")}</p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="d-flex flex-column flex-md-row gap-3 pt-3">
          <button
            className="btn btn-gradient flex-fill"
            onClick={handleSearch}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="d-flex align-items-center justify-content-center gap-2">
                <div className="spinner-border spinner-border-sm" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                Searching...
              </span>
            ) : (
              <span className="d-flex align-items-center justify-content-center gap-2">
                <Search style={{ width: "16px", height: "16px" }} />
                Find Other Sequences
              </span>
            )}
          </button>
          <button
            className="btn btn-outline-accent flex-fill"
            onClick={onUploadSequence}
            disabled={isLoading}
          >
            <Upload
              style={{ width: "16px", height: "16px" }}
              className="me-2"
            />
            Upload Pass Sequence
          </button>
        </div>
      </div>
    </div>
  );
};

export default FifaForm;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
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
`}</style>;
