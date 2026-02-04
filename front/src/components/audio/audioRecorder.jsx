// src/components/audio/AudioRecorder.js
import { useState, useRef, useEffect } from "react";
import { Mic, Square, Upload, FileAudio, X, Play, Pause } from "lucide-react";

const AudioRecorder = ({ onAudioReady }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeTab, setActiveTab] = useState("record");
  const [waveformBars, setWaveformBars] = useState(Array(20).fill(0.3));
  const [errorMsg, setErrorMsg] = useState(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null); // Restored
  const timerRef = useRef(null); // Restored

  // Restored timer and waveform logic
  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
        // Animate waveform
        setWaveformBars(
          Array(20)
            .fill(0)
            .map(() => 0.2 + Math.random() * 0.8),
        );
      }, 100);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      setWaveformBars(Array(20).fill(0.3));
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

  const handleStartRecording = async () => {
    setErrorMsg(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        onAudioReady(audioBlob);

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      if (err.name === "NotAllowedError") {
        setErrorMsg("Microphone access denied. Please allow microphone permissions.");
      } else if (err.name === "NotFoundError") {
        setErrorMsg("No microphone found. Please connect a microphone.");
      } else {
        setErrorMsg("Could not access microphone. " + err.message);
      }
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      onAudioReady(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === "audio/wav" || file.type === "audio/mpeg")) {
      setUploadedFile(file);
      const url = URL.createObjectURL(file);
      setAudioUrl(url);
      onAudioReady(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const formatTime = (centiseconds) => {
    const seconds = Math.floor(centiseconds / 10);
    const cs = centiseconds % 10;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}.${cs}`;
  };

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="card glass-card">
      <div className="card-header">
        <h5 className="card-title mb-0">Audio Input</h5>
      </div>
      <div className="card-body">
        <ul className="nav nav-tabs mb-4" id="audioTabs" role="tablist">
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === "record" ? "active" : ""}`}
              onClick={() => setActiveTab("record")}
              type="button"
            >
              <Mic style={{ width: "16px", height: "16px" }} className="me-2" />
              Record
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className={`nav-link ${activeTab === "upload" ? "active" : ""}`}
              onClick={() => setActiveTab("upload")}
              type="button"
            >
              <Upload
                style={{ width: "16px", height: "16px" }}
                className="me-2"
              />
              Upload
            </button>
          </li>
        </ul>

        <div className="tab-content">
          <div
            className={`tab-pane fade ${activeTab === "record" ? "show active" : ""}`}
          >
            {/* Error / Permission Message */}
            {errorMsg && (
              <div className="alert alert-danger py-2 mb-3 text-center small">
                {errorMsg}
              </div>
            )}

            {/* Waveform Visualization */}
            <div
              className="bg-light bg-opacity-25 rounded-3 d-flex align-items-center justify-content-center gap-1 px-4 mb-4"
              style={{ height: "96px" }}
            >
              {waveformBars.map((height, index) => (
                <div
                  key={index}
                  className="rounded-pill transition-all"
                  style={{
                    width: "8px",
                    height: `${height * 100}%`,
                    backgroundColor: isRecording ? "#667eea" : "#6c757d",
                    transitionDelay: `${index * 10}ms`,
                    transitionDuration: "100ms",
                  }}
                />
              ))}
            </div>

            {/* Timer */}
            <div className="text-center mb-4">
              <span className="display-6 fw-bold font-monospace">
                {formatTime(recordingTime)}
              </span>
            </div>

            {/* Record Button */}
            <div className="d-flex justify-content-center mb-3">
              {isRecording ? (
                <button
                  className="btn btn-danger rounded-circle position-relative"
                  style={{ width: "80px", height: "80px" }}
                  onClick={handleStopRecording}
                >
                  <div className="position-absolute top-0 start-0 w-100 h-100 rounded-circle bg-danger bg-opacity-30 pulse-ring" />
                  <Square style={{ width: "32px", height: "32px" }} />
                </button>
              ) : (
                <button
                  className="btn btn-gradient rounded-circle"
                  style={{ width: "80px", height: "80px" }}
                  onClick={handleStartRecording}
                >
                  <Mic style={{ width: "32px", height: "32px" }} />
                </button>
              )}
            </div>

            <p className="text-center text-muted small">
              {isRecording
                ? "Click to stop recording"
                : "Click to start recording your melody"}
            </p>
          </div>

          <div
            className={`tab-pane fade ${activeTab === "upload" ? "show active" : ""}`}
          >
            <div
              className="border-2 border-dashed border-secondary rounded-3 p-5 text-center hover-border-primary cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              style={{ transition: "all 0.3s ease" }}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="d-none"
                accept=".wav,.mp3,.m4a,.ogg,.flac,audio/*"
                onChange={handleFileUpload}
              />
              <div
                className="rounded-3 bg-primary bg-opacity-10 d-flex align-items-center justify-content-center mx-auto mb-4"
                style={{ width: "64px", height: "64px" }}
              >
                <FileAudio
                  style={{ width: "32px", height: "32px", color: "#667eea" }}
                />
              </div>
              <p className="fw-medium mb-2">Drop your audio file here</p>
              <p className="text-muted small mb-0">
                or click to browse (WAV, MP3, M4A, OGG, FLAC)
              </p>
            </div>

            {uploadedFile && (
              <div className="d-flex align-items-center justify-content-between p-3 bg-light rounded-3 mt-3">
                <div className="d-flex align-items-center gap-3">
                  <FileAudio
                    style={{ width: "20px", height: "20px", color: "#667eea" }}
                  />
                  <div>
                    <p className="fw-medium small mb-1">{uploadedFile.name}</p>
                    <p className="text-muted x-small mb-0">
                      {(uploadedFile.size / 1024).toFixed(1)} KB •{" "}
                      {uploadedFile.type}
                    </p>
                  </div>
                </div>
                <button
                  className="btn btn-link p-0"
                  onClick={() => setUploadedFile(null)}
                >
                  <X style={{ width: "16px", height: "16px" }} />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Audio Preview */}
        {audioUrl && (
          <div className="mt-4 p-3 bg-light rounded-3">
            <div className="d-flex justify-content-between align-items-center mb-2">
              <h6 className="mb-0">Audio Preview</h6>
              <button
                className="btn btn-sm btn-outline-primary"
                onClick={handlePlayPause}
              >
                {isPlaying ? (
                  <>
                    <Pause
                      style={{ width: "16px", height: "16px" }}
                      className="me-1"
                    />
                    Pause
                  </>
                ) : (
                  <>
                    <Play
                      style={{ width: "16px", height: "16px" }}
                      className="me-1"
                    />
                    Play
                  </>
                )}
              </button>
            </div>
            <audio
              ref={audioRef}
              src={audioUrl}
              controls
              className="w-100"
              onEnded={() => setIsPlaying(false)}
              onPause={() => setIsPlaying(false)}
              onPlay={() => setIsPlaying(true)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default AudioRecorder;
