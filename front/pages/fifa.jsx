import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Trophy } from "lucide-react";
import Layout from "@/components/layout/Layout";
import FifaForm from "@/components/fifa/FifaForm";
import FifaResults from "@/components/fifa/FifaResults";
import FootballPitch from "@/components/fifa/FootballPitch";
import PositionCharts from "@/components/fifa/PositionCharts";
import { Button } from "@/components/ui/button";
import {
  detectPassSequenceById,
  detectPassSequenceByMetadata,
  PassSequenceResult,
} from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const Fifa = () => {
  const [results, setResults] = useState([]);
  const [selectedResult, setSelectedResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [inputSequence, setInputSequence] = useState(null);

  const handleSearchByMetadata = async (data) => {
    setIsLoading(true);
    setSelectedResult(null);

    try {
      const response = await detectPassSequenceByMetadata(
        data.players,
        data.stage,
        data.group,
        data.date,
        data.match,
      );

      if (response.status === "success" && response.results) {
        setResults(response.results);
        // Set input sequence from first result for visualization
        if (response.results.length > 0) {
          setInputSequence(response.results[0].inputCoordinates);
        }
        toast({
          title: "Search Complete",
          description: `Found ${response.results.length} matching sequences.`,
        });
      } else {
        setResults([]);
        setInputSequence(null);
        toast({
          title: "No Matches Found",
          description: response.error || "Try adjusting your search criteria.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to search sequences. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSequence = async () => {
    setIsLoading(true);
    setSelectedResult(null);

    try {
      const response = await detectPassSequenceById("mock-sequence-id");

      if (response.status === "success" && response.results) {
        setResults(response.results);
        if (response.results.length > 0) {
          setInputSequence(response.results[0].inputCoordinates);
        }
        toast({
          title: "Upload Complete",
          description: "Sequence uploaded and analyzed successfully.",
        });
      } else {
        toast({
          title: "Upload Failed",
          description: "Could not analyze the uploaded sequence.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to upload sequence. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout>
      <div className="container-fluid py-5">
        {/* Header */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
              <div className="d-flex align-items-center gap-3">
                <Link to="/">
                  <Button
                    variant="light"
                    className="rounded-circle p-2 border-0"
                  >
                    <ArrowLeft style={{ width: "20px", height: "20px" }} />
                  </Button>
                </Link>
                <div>
                  <h1 className="h2 fw-bold text-dark d-flex align-items-center gap-3 mb-2">
                    <div
                      className="rounded-3 bg-gradient p-2 d-flex align-items-center justify-content-center"
                      style={{
                        width: "40px",
                        height: "40px",
                        background:
                          "linear-gradient(to bottom right, var(--accent), var(--accent-light))",
                      }}
                    >
                      <Trophy
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "var(--accent-foreground)",
                        }}
                      />
                    </div>
                    FIFA World Cup 2022 Sequence Detector
                  </h1>
                  <p className="text-muted mb-0">
                    Analyze and compare pass sequences from the World Cup
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="row g-4">
          {/* Input Form - Full Width */}
          <div className="col-12">
            <FifaForm
              onSearchByMetadata={handleSearchByMetadata}
              onUploadSequence={handleUploadSequence}
              isLoading={isLoading}
            />
          </div>

          {/* Matching Sequences */}
          <div className="col-12">
            <FifaResults
              results={results}
              selectedResult={selectedResult}
              onSelectResult={setSelectedResult}
              isLoading={isLoading}
            />
          </div>

          {/* Football Pitch */}
          <div className="col-12">
            <FootballPitch
              inputSequence={inputSequence}
              selectedResult={selectedResult}
            />
          </div>

          {/* Position Charts - Full Width */}
          <div className="col-12">
            <PositionCharts
              inputSequence={inputSequence}
              selectedResult={selectedResult}
            />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Fifa;

<style jsx>{`
  :root {
    --accent: #3b82f6;
    --accent-light: #93c5fd;
    --accent-foreground: #ffffff;
  }

  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }
`}</style>;
