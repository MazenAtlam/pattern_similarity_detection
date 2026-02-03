import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Music } from "lucide-react";
import Layout from "@/components/layout/Layout";
import AudioRecorder from "@/components/songs/AudioRecorder";
import SongResults from "@/components/songs/SongResults";
import { Button } from "@/components/ui/button";
import { detectSong } from "@/lib/api";
import { toast } from "@/hooks/use-toast";

const Songs = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleAudioReady = async (file) => {
    setIsLoading(true);
    try {
      const response = await detectSong(file);
      if (response.status === "success" && response.results) {
        setResults(response.results);
        toast({
          title: "Analysis Complete",
          description: `Found ${response.results.length} matching songs.`,
        });
      } else {
        toast({
          title: "No Matches Found",
          description: "Try recording or uploading a different melody.",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to analyze audio. Please try again.",
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
                          "linear-gradient(to bottom right, var(--primary), var(--primary-light))",
                      }}
                    >
                      <Music
                        style={{
                          width: "20px",
                          height: "20px",
                          color: "white",
                        }}
                      />
                    </div>
                    Humming Song Detector
                  </h1>
                  <p className="text-muted mb-0">
                    Record your melody or upload an audio file to find matching
                    songs
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="row g-4">
          <div className="col-lg-6">
            <AudioRecorder onAudioReady={handleAudioReady} />
          </div>
          <div className="col-lg-6">
            <SongResults results={results} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Songs;
