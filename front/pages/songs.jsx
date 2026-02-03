import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Music } from "lucide-react";
import Layout from "../src/components/layout/Layout";
import AudioRecorder from "../src/components/audio/AudioRecorder";
import SongResults from "../src/components/audio/SongResults";
import Button from "../src/components/ui/Button";
import { detectSong, mockDetectSong } from "../src/utils/api"; // Update the import path

// Toast notification function
const showToast = (title, message, type = "success") => {
  //   // Check if Bootstrap is loaded
  //   if (typeof bootstrap === "undefined") {
  //     console.warn("Bootstrap not loaded, showing alert instead");
  //     alert(`${title}: ${message}`);
  //     return;
  //   }

  const toastId = "custom-toast-" + Date.now();
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-bg-${type === "success" ? "success" : "danger"} border-0" role="alert" aria-live="assertive" aria-atomic="true">
      <div class="d-flex">
        <div class="toast-body">
          <strong>${title}</strong> - ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  // Get or create toast container
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    container.className = "position-fixed top-0 end-0 p-3";
    container.style.zIndex = "1060";
    document.body.appendChild(container);
  }

  container.insertAdjacentHTML("beforeend", toastHtml);

  // Initialize and show the toast
  const toastElement = document.getElementById(toastId);
  const toast = new bootstrap.Toast(toastElement);
  toast.show();

  // Remove toast from DOM after it's hidden
  toastElement.addEventListener("hidden.bs.toast", () => {
    toastElement.remove();
  });
};

const Songs = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [useMockAPI, setUseMockAPI] = useState(true); // Toggle between mock and real API

  const handleAudioReady = async (file) => {
    setIsLoading(true);
    try {
      let response;

      if (useMockAPI) {
        // Use mock API for development
        response = await mockDetectSong(file);
      } else {
        // Use real API
        response = await detectSong(file);
      }

      if (response.status === "success") {
        // Map API response to component format
        const mappedResults = response.results.map((song, index) => ({
          id: index + 1,
          songName: song.song_name,
          artist: song.artist,
          album: "", // API doesn't provide album info
          similarityIndex: Math.round(song.similarity_index * 100), // Convert to percentage
          fileUrl: song.file_url,
        }));

        setResults(mappedResults);
        showToast(
          "Analysis Complete",
          `Found ${response.matched_songs_found || response.results.length} matching songs.`,
          "success",
        );
      } else {
        showToast(
          "No Matches Found",
          response.error || "Try recording or uploading a different melody.",
          "error",
        );
        setResults([]);
      }
    } catch (error) {
      console.error("Error analyzing audio:", error);
      showToast(
        "Error",
        error.message || "Failed to analyze audio. Please try again.",
        "error",
      );
      setResults([]);
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
                          "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
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

              {/* API Mode Toggle */}
              <div className="d-flex align-items-center gap-2 mt-3 mt-md-0">
                <span className="text-muted small">API Mode:</span>
                <div className="btn-group btn-group-sm" role="group">
                  <button
                    type="button"
                    className={`btn ${useMockAPI ? "btn-primary" : "btn-outline-primary"}`}
                    onClick={() => setUseMockAPI(true)}
                  >
                    Mock API
                  </button>
                  <button
                    type="button"
                    className={`btn ${!useMockAPI ? "btn-primary" : "btn-outline-primary"}`}
                    onClick={() => setUseMockAPI(false)}
                  >
                    Real API
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Loading Indicator */}
        {isLoading && (
          <div className="row mb-4">
            <div className="col-12">
              <div className="alert alert-info d-flex align-items-center">
                <div
                  className="spinner-border spinner-border-sm me-3"
                  role="status"
                >
                  <span className="visually-hidden">Loading...</span>
                </div>
                <div>
                  <strong>Analyzing your audio...</strong>
                  <p className="mb-0 small">
                    This may take a few seconds. Please wait.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        <div className="row g-4">
          <div className="col-lg-6">
            <AudioRecorder onAudioReady={handleAudioReady} />
          </div>
          <div className="col-lg-6">
            <SongResults results={results} isLoading={isLoading} />
          </div>
        </div>

        {/* API Info */}
        <div className="row mt-4">
          <div className="col-12">
            <div
              className={`alert ${useMockAPI ? "alert-warning" : "alert-success"}`}
            >
              <h5 className="alert-heading">
                {useMockAPI ? "Using Mock API" : "Using Real API"}
              </h5>
              <p className="mb-0">
                {useMockAPI
                  ? 'Currently using mock data for demonstration. Switch to "Real API" when your backend is running.'
                  : "Connected to real API endpoint. Make sure your backend server is running."}
              </p>
              {!useMockAPI && (
                <div className="mt-2">
                  <small className="text-muted">
                    API Endpoint: <code>POST /api/v1/songs/detect</code>
                  </small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Songs;
