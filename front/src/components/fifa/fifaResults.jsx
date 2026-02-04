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
    if (percentage >= 80) return 'text-green-500';
    if (percentage >= 60) return 'text-yellow-500';
    return 'text-red-500';
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
    <div className="card glass-card p-6 mt-6">
      <div className="card-header">
        <h5 className="card-title text-xl font-bold mb-4">Matching Sequences</h5>
      </div>
      <div className="card-body">
        <div className="overflow-x-auto">
          <table className="table w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="p-3">Index</th>
                <th className="p-3">Sequence Start Time</th>
                <th className="p-3">Similarity Measure</th>
              </tr>
            </thead>
            <tbody>
              {paginatedResults.map((result, index) => {
                const globalIndex = (currentPage - 1) * itemsPerPage + index + 1;
                return (
                  <tr
                    key={index}
                    className={`border-b border-gray-800 hover:bg-white/5 cursor-pointer transition-colors ${selectedResult === result ? 'bg-blue-500/20 border-l-4 border-l-blue-500' : ''}`}
                    onClick={() => onSelectResult && onSelectResult(result)}
                  >
                    <td className="p-3 font-mono text-gray-400">#{globalIndex}</td>
                    <td className="p-3">{result.sequence_start_time}</td>
                    <td className="p-3">
                      <span className={`font-bold ${getSimilarityColor(result.similarity_measure)}`}>
                        {result.similarity_measure.toFixed(4)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination: "Previous < X > Next" */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 mt-6">
            <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Previous</span>

            <button
              type="button"
              className="p-1 rounded hover:bg-white/10 disabled:opacity-30 transition-colors"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            <span className="font-bold text-lg min-w-[20px] text-center">
              {currentPage}
            </span>

            <button
              type="button"
              className="p-1 rounded hover:bg-white/10 disabled:opacity-30 transition-colors"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="w-5 h-5" />
            </button>

            <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Next</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default FifaResults;