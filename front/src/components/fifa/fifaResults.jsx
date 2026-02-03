import { useState } from 'react';
import { ArrowRight, Trophy, ChevronLeft, ChevronRight } from 'lucide-react';
import '../../../styles/FifaResults.css';

const FifaResults = ({ results, selectedResult, onSelectResult, isLoading }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const totalPages = Math.ceil(results.length / itemsPerPage);
  const paginatedResults = results.slice(
      (currentPage - 1) * itemsPerPage,
      currentPage * itemsPerPage
  );

  const getSimilarityColor = (similarity) => {
    if (similarity >= 80) return 'high';
    if (similarity >= 60) return 'medium';
    return 'low';
  };

  if (isLoading) {
    return (
        <div className="fifa-results-card">
          <div className="card-header-custom">
            <h3 className="card-title-custom">Matching Sequences</h3>
          </div>
          <div className="card-content-custom">
            <div className="loading-state">
              <div className="loading-spinner-container">
                <div className="loading-spinner" />
              </div>
              <p className="state-message">Finding similar sequences...</p>
            </div>
          </div>
        </div>
    );
  }

  if (results.length === 0) {
    return (
        <div className="fifa-results-card">
          <div className="card-header-custom">
            <h3 className="card-title-custom">Matching Sequences</h3>
          </div>
          <div className="card-content-custom">
            <div className="empty-state">
              <div className="empty-icon-container">
                <Trophy className="empty-icon" />
              </div>
              <p className="state-message">
                Search for pass sequences to see matching results
              </p>
            </div>
          </div>
        </div>
    );
  }

  return (
      <div className="fifa-results-card">
        <div className="card-header-custom">
          <h3 className="card-title-custom">Matching Sequences</h3>
        </div>
        <div className="card-content-custom">
          <div className="table-container">
            <table className="results-table">
              <thead>
              <tr className="table-header-row">
                <th className="table-header-cell" style={{ width: '48px' }}>#</th>
                <th className="table-header-cell">Match</th>
                <th className="table-header-cell">Stage</th>
                <th className="table-header-cell" style={{ width: '120px' }}>Similarity</th>
                <th className="table-header-cell d-none d-lg-table-cell">Sequence</th>
              </tr>
              </thead>
              <tbody>
              {paginatedResults.map((result, index) => (
                  <tr
                      key={result.id}
                      className={`table-row ${selectedResult?.id === result.id ? 'selected' : ''}`}
                      onClick={() => onSelectResult(result)}
                  >
                    <td className="table-cell">
                      {(currentPage - 1) * itemsPerPage + index + 1}
                    </td>
                    <td className="table-cell match-info">
                      <p className="match-teams">{result.teams}</p>
                      <p className="match-date">{result.date}</p>
                    </td>
                    <td className="table-cell stage-info">
                      {result.stage}
                    </td>
                    <td className="table-cell similarity-container">
                    <span className={`similarity-value ${getSimilarityColor(result.similarityIndex)}`}>
                      {result.similarityIndex.toFixed(1)}%
                    </span>
                      <div className="progress-bar-custom">
                        <div
                            className={`progress-fill ${getSimilarityColor(result.similarityIndex)}`}
                            style={{ width: `${result.similarityIndex}%` }}
                        />
                      </div>
                    </td>
                    <td className="table-cell d-none d-lg-table-cell">
                      <div className="sequence-flow">
                        {result.sequenceFlow.slice(0, 3).map((player, i) => (
                            <span key={i} className="player-container">
                          <span className="player-name">{player}</span>
                              {i < Math.min(result.sequenceFlow.length - 1, 2) && (
                                  <ArrowRight className="sequence-arrow" />
                              )}
                        </span>
                        ))}
                        {result.sequenceFlow.length > 3 && (
                            <span className="ellipsis">...</span>
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
              <div className="pagination-container">
                <div className="pagination-buttons">
                  <button
                      type="button"
                      className="pagination-button"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                  >
                    <ChevronLeft style={{ width: '16px', height: '16px' }} />
                    Previous
                  </button>
                  <span className="page-number">
                {currentPage}
              </span>
                  <button
                      type="button"
                      className="pagination-button"
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                  >
                    Next
                    <ChevronRight style={{ width: '16px', height: '16px' }} />
                  </button>
                </div>
                <p className="pagination-info">
                  Showing {(currentPage - 1) * itemsPerPage + 1} to{' '}
                  {Math.min(currentPage * itemsPerPage, results.length)} of{' '}
                  {results.length} results
                </p>
              </div>
          )}
        </div>
      </div>
  );
};

export default FifaResults;