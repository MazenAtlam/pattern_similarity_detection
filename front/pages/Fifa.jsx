import { useState } from "react";
import Layout from "../src/components/layout/Layout";
import FifaForm from "../src/components/fifa/fifaForm";
import FifaResults from "../src/components/fifa/fifaResults";
import FootballPitch from "../src/components/fifa/FootballPitch";
import PositionCharts from "../src/components/fifa/PositionCharts";
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
      similarityIndex: (item.similarity_measure || 0) * 100, // Convert 0-1 to 0-100%
      sequenceFlow: item.player_sequence || ["Player A", "Player B", "Player C"], // Mock if missing
      matchCoordinates: item.sequence_events ? item.sequence_events.map((evt, i) => ({
        time: i, // Mock time steps if not provided
        x: evt.x,
        y: evt.y
      })) : []
    }));
  };

  const handleSearchByMetadata = async (data) => {
    setIsLoading(true);
    setError(null);
    setSelectedResult(null);

    try {
      // Constructing payload based on form data
      const payload = {
        stage: data.stage,
        group: data.group,
        date: data.date,
        match: data.match,
        players: data.players
      };

      const response = await detectPassSequence(payload);

      if (response.status === 'success' && response.pass_sequences_data) {
        const mappedResults = mapApiResults(response);
        setResults(mappedResults);

        // Set input sequence for visualization (Mocking input coordinates for demo)
        const mockInputCoords = data.players.map((_, i) => ({
          time: i,
          x: 50 + Math.random() * 20 - 10,
          y: 50 + Math.random() * 20 - 10
        }));
        setInputSequence(mockInputCoords);

      } else {
        setResults([]);
        setInputSequence(null);
        setError(response.error || 'No matching sequences found.');
      }
    } catch (err) {
      setError(err.message || 'Failed to search sequences. Please try again.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSequence = async () => {
    setIsLoading(true);
    setError(null);
    setSelectedResult(null);

    try {
      // Using the example payload from the prompt
      const payload = {
        sequence_path: "/data/2022/final/arg_fra_seq_002.pkl"
      };

      const response = await detectPassSequence(payload);

      if (response.status === 'success' && response.pass_sequences_data) {
        const mappedResults = mapApiResults(response);
        setResults(mappedResults);

        // Use the first result's coordinates as a mock input for visualization demonstration
        if (mappedResults.length > 0) {
          setInputSequence(mappedResults[0].matchCoordinates.map(p => ({...p, x: p.x + 5, y: p.y - 5})));
        }
      } else {
        setError(response.error || 'Could not analyze the sequence.');
      }
    } catch (err) {
      setError(err.message || 'Failed to upload/analyze sequence.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
      <Layout
          pageTitle="FIFA World Cup 2022 Sequence Detector"
          pageDescription="Analyze and compare pass sequences from the World Cup"
      >
        <div className="fifa-container">
          <div className="container">
            {/* Loading Overlay */}
            {isLoading && (
                <div className="loading-overlay">
                  <div className="loading-spinner"></div>
                </div>
            )}

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
                />
              </div>
            )}

            {/* Football Pitch */}
            {(inputSequence || selectedResult) && (
              <div className="pitch-section">
                <FootballPitch
                  inputSequence={inputSequence}
                  selectedResult={selectedResult}
                />
              </div>
            )}

            {/* Position Charts - Full Width */}
            {(inputSequence || selectedResult) && (
              <div className="charts-section">
                <PositionCharts
                  inputSequence={inputSequence}
                  selectedResult={selectedResult}
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
