import { useState } from "react";
import { Play, Pause, ChevronLeft, ChevronRight, Music2 } from "lucide-react";

const SongResults = ({ results, isLoading }) => {
  const [playingId, setPlayingId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const sortedResults = [...results].sort(
    (a, b) => b.similarityIndex - a.similarityIndex,
  );
  const totalPages = Math.ceil(sortedResults.length / itemsPerPage);
  const paginatedResults = sortedResults.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage,
  );

  const handlePlayPause = (id) => {
    setPlayingId(playingId === id ? null : id);
  };

  const getSimilarityColor = (similarity) => {
    if (similarity >= 80) return "text-success";
    if (similarity >= 60) return "text-warning";
    return "text-muted";
  };

  if (isLoading) {
    return (
      <div className="card glass-card">
        <div className="card-header">
          <h5 className="card-title mb-0">Detection Results</h5>
        </div>
        <div className="card-body">
          <div className="d-flex flex-column align-items-center justify-content-center py-5 gap-3">
            <div className="rounded-3 bg-primary bg-opacity-10 d-flex align-items-center justify-content-center p-3">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
            <p className="text-muted">Analyzing your melody...</p>
          </div>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="card glass-card">
        <div className="card-header">
          <h5 className="card-title mb-0">Detection Results</h5>
        </div>
        <div className="card-body">
          <div className="d-flex flex-column align-items-center justify-content-center py-5 gap-3">
            <div className="rounded-3 bg-secondary bg-opacity-10 d-flex align-items-center justify-content-center p-3">
              <Music2
                style={{ width: "32px", height: "32px" }}
                className="text-muted"
              />
            </div>
            <p className="text-muted">
              Record or upload an audio file to see matching songs
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card glass-card">
      <div className="card-header">
        <h5 className="card-title mb-0">Detection Results</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr>
                <th style={{ width: "48px" }}>#</th>
                <th>Song</th>
                <th>Artist</th>
                <th style={{ width: "160px" }}>Similarity</th>
                <th style={{ width: "96px" }} className="text-center">
                  Play
                </th>
              </tr>
            </thead>
            <tbody>
              {paginatedResults.map((song, index) => (
                <tr key={song.id}>
                  <td className="fw-medium text-muted">
                    {(currentPage - 1) * itemsPerPage + index + 1}
                  </td>
                  <td>
                    <div className="d-flex align-items-center gap-3">
                      <div
                        className="rounded bg-gradient d-flex align-items-center justify-content-center"
                        style={{
                          width: "40px",
                          height: "40px",
                          background:
                            "linear-gradient(to bottom right, var(--primary-light), var(--accent-light))",
                        }}
                      >
                        <Music2
                          style={{
                            width: "20px",
                            height: "20px",
                            color: "var(--primary)",
                          }}
                        />
                      </div>
                      <div>
                        <p className="fw-medium mb-1">{song.songName}</p>
                        {song.album && (
                          <p className="text-muted small mb-0">{song.album}</p>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="text-muted">{song.artist}</td>
                  <td>
                    <div className="d-flex flex-column gap-1">
                      <div className="d-flex align-items-center justify-content-between">
                        <span
                          className={`fw-bold ${getSimilarityColor(song.similarityIndex)}`}
                        >
                          {song.similarityIndex.toFixed(1)}%
                        </span>
                      </div>
                      <div className="progress" style={{ height: "8px" }}>
                        <div
                          className="progress-bar"
                          role="progressbar"
                          style={{ width: `${song.similarityIndex}%` }}
                          aria-valuenow={song.similarityIndex}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        />
                      </div>
                    </div>
                  </td>
                  <td className="text-center">
                    <button
                      className="btn btn-outline-primary btn-sm rounded-circle"
                      onClick={() => handlePlayPause(song.id)}
                    >
                      {playingId === song.id ? (
                        <Pause style={{ width: "16px", height: "16px" }} />
                      ) : (
                        <Play style={{ width: "16px", height: "16px" }} />
                      )}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="d-flex flex-column align-items-center gap-3 mt-4 pt-3 border-top">
            <div className="d-flex align-items-center gap-2">
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft style={{ width: "16px", height: "16px" }} />
                Previous
              </button>
              <span className="fw-medium px-3">{currentPage}</span>
              <button
                className="btn btn-outline-secondary btn-sm"
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages}
              >
                Next
                <ChevronRight style={{ width: "16px", height: "16px" }} />
              </button>
            </div>
            <p className="text-muted small mb-0">
              Showing {(currentPage - 1) * itemsPerPage + 1} to{" "}
              {Math.min(currentPage * itemsPerPage, sortedResults.length)} of{" "}
              {sortedResults.length} results
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SongResults;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }

  :root {
    --primary: #3b82f6;
    --primary-light: #93c5fd;
    --accent-light: #c4b5fd;
  }
`}</style>;
