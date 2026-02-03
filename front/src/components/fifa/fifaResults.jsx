import { useState } from "react";
import { ArrowRight, Trophy, ChevronLeft, ChevronRight } from "lucide-react";

const FifaResults = ({
  results,
  selectedResult,
  onSelectResult,
  isLoading,
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const totalPages = Math.ceil(results.length / itemsPerPage);
  const paginatedResults = results.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage,
  );

  const getSimilarityColor = (similarity) => {
    if (similarity >= 80) return "text-success";
    if (similarity >= 60) return "text-warning";
    return "text-muted";
  };

  if (isLoading) {
    return (
      <div className="card glass-card h-100">
        <div className="card-header">
          <h5 className="card-title mb-0">Matching Sequences</h5>
        </div>
        <div className="card-body">
          <div className="d-flex flex-column align-items-center justify-content-center py-5 gap-3">
            <div className="rounded-3 bg-accent bg-opacity-10 d-flex align-items-center justify-content-center p-3">
              <div className="spinner-border text-accent" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
            <p className="text-muted">Finding similar sequences...</p>
          </div>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="card glass-card h-100">
        <div className="card-header">
          <h5 className="card-title mb-0">Matching Sequences</h5>
        </div>
        <div className="card-body">
          <div className="d-flex flex-column align-items-center justify-content-center py-5 gap-3">
            <div className="rounded-3 bg-secondary bg-opacity-10 d-flex align-items-center justify-content-center p-3">
              <Trophy
                style={{ width: "32px", height: "32px" }}
                className="text-muted"
              />
            </div>
            <p className="text-muted text-center">
              Search for pass sequences to see matching results
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card glass-card h-100">
      <div className="card-header">
        <h5 className="card-title mb-0">Matching Sequences</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover">
            <thead>
              <tr>
                <th style={{ width: "48px" }}>#</th>
                <th>Match</th>
                <th>Stage</th>
                <th style={{ width: "112px" }}>Similarity</th>
                <th className="d-none d-lg-table-cell">Sequence</th>
              </tr>
            </thead>
            <tbody>
              {paginatedResults.map((result, index) => (
                <tr
                  key={result.id}
                  className={`cursor-pointer ${selectedResult?.id === result.id ? "table-active" : ""}`}
                  onClick={() => onSelectResult(result)}
                  style={{ cursor: "pointer" }}
                >
                  <td className="fw-medium text-muted">
                    {(currentPage - 1) * itemsPerPage + index + 1}
                  </td>
                  <td>
                    <div>
                      <p className="fw-medium mb-1">{result.teams}</p>
                      <p className="text-muted small mb-0">{result.date}</p>
                    </div>
                  </td>
                  <td className="text-muted">{result.stage}</td>
                  <td>
                    <div className="d-flex flex-column gap-1">
                      <span
                        className={`fw-bold ${getSimilarityColor(result.similarityIndex)}`}
                      >
                        {result.similarityIndex.toFixed(1)}%
                      </span>
                      <div className="progress" style={{ height: "6px" }}>
                        <div
                          className="progress-bar"
                          role="progressbar"
                          style={{ width: `${result.similarityIndex}%` }}
                          aria-valuenow={result.similarityIndex}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        />
                      </div>
                    </div>
                  </td>
                  <td className="d-none d-lg-table-cell">
                    <div
                      className="d-flex align-items-center gap-1 text-muted small"
                      style={{ maxWidth: "200px" }}
                    >
                      {result.sequenceFlow.slice(0, 3).map((player, i) => (
                        <span
                          key={i}
                          className="d-flex align-items-center gap-1 text-nowrap"
                        >
                          {player}
                          {i < Math.min(result.sequenceFlow.length - 1, 2) && (
                            <ArrowRight
                              style={{
                                width: "12px",
                                height: "12px",
                                color: "var(--primary)",
                              }}
                            />
                          )}
                        </span>
                      ))}
                      {result.sequenceFlow.length > 3 && (
                        <span className="text-muted">...</span>
                      )}
                    </div>
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
              {Math.min(currentPage * itemsPerPage, results.length)} of{" "}
              {results.length} results
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FifaResults;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }

  .cursor-pointer {
    cursor: pointer;
  }
`}</style>;
