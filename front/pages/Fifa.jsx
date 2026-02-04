import { useState } from "react";
import Layout from "../src/components/layout/Layout";
import FifaForm from "../src/components/fifa/fifaForm";
import FifaResults from "../src/components/fifa/fifaResults";
import FootballPitch from "../src/components/fifa/FootballPitch";
import "../styles/Fifa.css";

const Fifa = () => {
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [inputSequence, setInputSequence] = useState(null);
  const [error, setError] = useState(null);

  // Helper to map API response to UI format
  const mapApiResults = (apiData) => {
    if (!apiData || !apiData.pass_sequences_data) return [];

    return apiData.pass_sequences_data.map((item, index) => ({
      id: index, // Use a unique ID if available from backend
      teams: item.match_name || "Unknown Match", // Fallback if not provided
      date: item.match_date || "Unknown Date", // Fallback
      stage: item.match_stage || "Unknown Stage", // Fallback
      similarityIndex: (item.similarity_measure || 0) * 100, // Keep for legacy if needed
      similarity_measure: item.similarity_measure || 0, // Raw measure for table
      sequence_start_time: item.sequence_start_time || "00:00",
      sequenceFlow: item.player_sequence || ["Player A", "Player B", "Player C"], // Mock if missing
      matchCoordinates: item.sequence_events ? item.sequence_events.map((evt, i) => ({
        time: i, // Mock time steps if not provided
        x: evt.x,
        y: evt.y
      })) : []
    }));
  };

  const handleSearchStart = () => {
    setIsLoading(true);
    setError(null);
  };

  const handleReset = () => {
    setResults([]);
    setInputSequence(null);
    setSelectedResult(null);
    setError(null);
    // Do NOT set isLoading to false here if it was caused by reset, but slider change implies user interaction which stops any previous flow or just resets view.
    // Actually, if we reset, we want the cards to disappear.
    // So results=[] means cards defined by "results.length > 0" will disappear.
  };

  const handleSearchSuccess = (response) => {
    setIsLoading(false); // Stop loading
    if (!response) return;

    // 1. Map and set matching results
    const mappedResults = mapApiResults(response);
    setResults(mappedResults);

    // 2. Set input sequence from backend response
    if (response.query_sequence_events) {
      const inputCoords = response.query_sequence_events.map((evt, i) => ({
        time: i,
        x: evt.x,
        y: evt.y
      }));
      setInputSequence(inputCoords);
    } else {
      setInputSequence(null);
    }
  };

  return (
    <Layout
      pageName="fifa"
      pageTitle="FIFA World Cup 2022 Sequence Detector"
      pageDescription="Analyze and compare pass sequences from the World Cup"
    >
      <div className="fifa-container">
        <div className="container">
          {/* Loading Overlay - REMOVE global overlay since we want in-card loading */}
          {/* 
          {isLoading && (
            <div className="loading-overlay">
              <div className="loading-spinner"></div>
            </div>
          )} 
          */}

          {/* Error Toast / Alert Placeholder */}
          {error && (
            <div className="alert alert-danger mb-4 mx-3 mx-lg-0" role="alert">
              {error}
            </div>
          )}

          {/* Content */}
          <div>
            {/* Input Form - Full Width */}
            <div className="form-section">
              <FifaForm
                isLoading={isLoading}
                onSearchSuccess={handleSearchSuccess}
                onSearchStart={handleSearchStart}
                onReset={handleReset}
              />
            </div>

            {/* Results Section - Show if results exist OR if Loading (to show spinner inside) */}
            {(isLoading || (results && results.length > 0)) && (
              <div className="results-section mb-6">
                <FifaResults
                  results={results}
                  selectedResult={selectedResult}
                  onSelectResult={setSelectedResult}
                  isLoading={isLoading}
                />
              </div>
            )}

            {/* Football Pitch - Show if (Input OR Result) Exists OR Loading */}
            {(isLoading || inputSequence || selectedResult) && (
              <div className="pitch-section">
                <FootballPitch
                  inputSequence={inputSequence}
                  selectedResult={selectedResult}
                  isLoading={isLoading}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Fifa;
