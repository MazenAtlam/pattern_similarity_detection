import { useState, useMemo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import '../../../styles/FifaResults.css';

const FifaResults = ({ results, selectedResult, onSelectResult, isLoading }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  // Sort results by similarity_measure relative to descending order
  // Assuming similarity_measure is 0-1, or higher is better. Use float.
  const sortedResults = useMemo(() => {
    if (!results) return [];
    return [...results].sort((a, b) => b.similarity_measure - a.similarity_measure);
  }, [results]);

  const totalPages = Math.ceil(sortedResults.length / itemsPerPage);
  const paginatedResults = sortedResults.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const getSimilarityColor = (similarity) => {
    // similarity is 0-1 range based on backed (1/1+dist)
    const percentage = similarity * 100;
    if (percentage >= 80) return 'text-success';
    if (percentage >= 60) return 'text-warning';
    return 'text-danger';
  };

  if (isLoading) {
    return (
      <div className="card glass-card h-100 flex items-center justify-center p-6 mt-6" style={{ minHeight: '200px' }}>
        <div className="flex flex-col items-center">
          <div className="spinner-border text-primary mb-3" role="status" style={{ width: '3rem', height: '3rem' }}>
            <span className="visually-hidden">Loading...</span>
          </div>
          <span className="text-muted">Searching...</span>
        </div>
      </div>
    );
  }



  if (!results || results.length === 0) {
    return null; // Do not show empty card if no results yet, or show placeholder? User said "use the response to list", implying when response exists.
  }

  return (
    <div className="card glass-card">
      <div className="card-header">
        <h5 className="card-title mb-0">Matching Sequences</h5>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-hover align-middle">
            <thead>
              <tr>
                <th style={{ width: "60px" }}>Index</th>
                <th>Sequence Start Time</th>
                <th>Similarity Measure</th>
              </tr>
            </thead>
            <tbody>
              {paginatedResults.map((result, index) => {
                const globalIndex = (currentPage - 1) * itemsPerPage + index + 1;
                const isSelected = selectedResult === result;
                return (
                  <tr
                    key={index}
                    onClick={() => onSelectResult && onSelectResult(result)}
                    style={{ cursor: 'pointer' }}
                    className={isSelected ? "table-active border-start border-4 border-primary" : ""}
                  >
                    <td className="fw-medium text-muted">#{globalIndex}</td>
                    <td>{result.sequence_start_time}</td>
                    <td>
                      <span className={`fw-bold ${getSimilarityColor(result.similarity_measure)}`}>
                        {result.similarity_measure.toFixed(4)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination from SongResults */}
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
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
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

export default FifaResults;