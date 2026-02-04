import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft, Music } from "lucide-react";
import Layout from "../src/components/layout/Layout";
import AudioRecorder from "../src/components/audio/AudioRecorder";
import SongResults from "../src/components/audio/SongResults";
import Button from "../src/components/ui/Button";
import { detectSong } from "../src/utils/api"; // Update the import path

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

  // // Initialize and show the toast
  // const toastElement = document.getElementById(toastId);
  // const toast = new bootstrap.Toast(toastElement);
  // toast.show();
  //
  // // Remove toast from DOM after it's hidden
  // toastElement.addEventListener("hidden.bs.toast", () => {
  //   toastElement.remove();
  // });
};

const Songs = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleAudioReady = async (file) => {
    setIsLoading(true);
    try {
      let response;

      // Use real API
      response = await detectSong(file);

      console.log(response);
      if (response.status === "success") {
        // Map API response to component format
        const mappedResults = response.results.map((song, index) => ({
          id: index + 1,
          songName: song.song_name,
          artist: song.artist,
          album: "", // API doesn't provide album info
          similarityIndex: Math.round(song.similarity_index),
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
    <Layout
      pageName="songs"
      pageTitle="Humming Song Detector"
      pageDescription="Record your melody or upload an audio file to find matching songs"
    >
      <div className="container-fluid py-5">
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
      </div>
    </Layout>
  );
};

export default Songs;
