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

  // const handleSearchByMetadata = async (data) => {
  //   setIsLoading(true);
  //   setSelectedResult(null);
  //
  //   try {
  //     const response = await detectPassSequenceByMetadata(
  //         data.players,
  //         data.stage,
  //         data.group,
  //         data.date,
  //         data.match
  //     );
  //
  //     if (response.status === 'success' && response.results) {
  //       setResults(response.results);
  //       // Set input sequence from first result for visualization
  //       if (response.results.length > 0) {
  //         setInputSequence(response.results[0].inputCoordinates);
  //       }
  //       toast({
  //         title: 'Search Complete',
  //         description: `Found ${response.results.length} matching sequences.`,
  //       });
  //     } else {
  //       setResults([]);
  //       setInputSequence(null);
  //       toast({
  //         title: 'No Matches Found',
  //         description: response.error || 'Try adjusting your search criteria.',
  //         variant: 'destructive',
  //       });
  //     }
  //     // eslint-disable-next-line no-unused-vars
  //   } catch (error) {
  //     toast({
  //       title: 'Error',
  //       description: 'Failed to search sequences. Please try again.',
  //       variant: 'destructive',
  //     });
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };
  //
  // const handleUploadSequence = async () => {
  //   setIsLoading(true);
  //   setSelectedResult(null);
  //
  //   try {
  //     const response = await detectPassSequenceById('mock-sequence-id');
  //
  //     if (response.status === 'success' && response.results) {
  //       setResults(response.results);
  //       if (response.results.length > 0) {
  //         setInputSequence(response.results[0].inputCoordinates);
  //       }
  //       toast({
  //         title: 'Upload Complete',
  //         description: 'Sequence uploaded and analyzed successfully.',
  //       });
  //     } else {
  //       toast({
  //         title: 'Upload Failed',
  //         description: 'Could not analyze the uploaded sequence.',
  //         variant: 'destructive',
  //       });
  //     }
  //     // eslint-disable-next-line no-unused-vars
  //   } catch (error) {
  //     toast({
  //       title: 'Error',
  //       description: 'Failed to upload sequence. Please try again.',
  //       variant: 'destructive',
  //     });
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

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

          {/* Content */}
          <div>
            {/* Input Form - Full Width */}
            <div className="form-section">
              <FifaForm
                // onSearchByMetadata={handleSearchByMetadata}
                // onUploadSequence={handleUploadSequence}
                isLoading={isLoading}
              />
            </div>

            {/* Matching Sequences */}
            {results.length > 0 && (
              <div className="results-section">
                <FifaResults
                  results={results}
                  selectedResult={selectedResult}
                  onSelectResult={setSelectedResult}
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
