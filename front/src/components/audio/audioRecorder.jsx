import { useState, useRef, useEffect } from "react";
import { Mic, Square, Upload, FileAudio, X } from "lucide-react";

const AudioRecorder = ({ onAudioReady }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [waveformBars, setWaveformBars] = useState(Array(20).fill(0.3));
  const fileInputRef = useRef(null);
  const timerRef = useRef();

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

  const handleStartRecording = () => {
    setIsRecording(true);
    setRecordingTime(0);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    // Simulate creating a blob
    const mockBlob = new Blob(["mock audio data"], { type: "audio/wav" });
    onAudioReady(mockBlob);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      onAudioReady(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type === "audio/wav" || file.type === "audio/mpeg")) {
      setUploadedFile(file);
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

  return (
    <div className="card glass-card">
      <div className="card-header">
        <h5 className="card-title mb-0">Audio Input</h5>
      </div>
      <div className="card-body">
        <ul className="nav nav-tabs mb-4" role="tablist">
          <li className="nav-item" role="presentation">
            <button
              className="nav-link active"
              id="record-tab"
              data-bs-toggle="tab"
              data-bs-target="#record"
              type="button"
              role="tab"
            >
              <Mic style={{ width: "16px", height: "16px" }} className="me-2" />
              Record
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button
              className="nav-link"
              id="upload-tab"
              data-bs-toggle="tab"
              data-bs-target="#upload"
              type="button"
              role="tab"
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
            className="tab-pane fade show active"
            id="record"
            role="tabpanel"
          >
            {/* Waveform Visualization */}
            <div
              className="bg-light rounded-3 d-flex align-items-center justify-content-center gap-1 px-4 mb-4"
              style={{ height: "96px" }}
            >
              {waveformBars.map((height, index) => (
                <div
                  key={index}
                  className="rounded-pill transition-all"
                  style={{
                    width: "8px",
                    height: `${height * 100}%`,
                    backgroundColor: isRecording
                      ? "var(--primary)"
                      : "var(--gray-400)",
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

          <div className="tab-pane fade" id="upload" role="tabpanel">
            <div
              className="border-2 border-dashed rounded-3 p-5 text-center hover-border-primary cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
            >
              <input
                type="file"
                ref={fileInputRef}
                className="d-none"
                accept=".wav,.mp3,audio/wav,audio/mpeg"
                onChange={handleFileUpload}
              />
              <div
                className="rounded-3 bg-primary bg-opacity-10 d-flex align-items-center justify-content-center mx-auto mb-4"
                style={{ width: "64px", height: "64px" }}
              >
                <FileAudio
                  style={{
                    width: "32px",
                    height: "32px",
                    color: "var(--primary)",
                  }}
                />
              </div>
              <p className="fw-medium mb-2">Drop your audio file here</p>
              <p className="text-muted small mb-0">
                or click to browse (.wav, .mp3)
              </p>
            </div>

            {uploadedFile && (
              <div className="d-flex align-items-center justify-content-between p-3 bg-light rounded-3 mt-3">
                <div className="d-flex align-items-center gap-3">
                  <FileAudio
                    style={{
                      width: "20px",
                      height: "20px",
                      color: "var(--primary)",
                    }}
                  />
                  <div>
                    <p className="fw-medium small mb-1">{uploadedFile.name}</p>
                    <p className="text-muted x-small mb-0">
                      {(uploadedFile.size / 1024).toFixed(1)} KB
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
      </div>
    </div>
  );
};

export default AudioRecorder;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }

  .btn-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
  }

  .hover-border-primary:hover {
    border-color: var(--primary) !important;
    background-color: rgba(var(--primary-rgb), 0.05);
  }

  .cursor-pointer {
    cursor: pointer;
  }

  .pulse-ring {
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% {
      transform: scale(0.95);
      opacity: 0.7;
    }
    50% {
      transform: scale(1.05);
      opacity: 0.3;
    }
    100% {
      transform: scale(0.95);
      opacity: 0.7;
    }
  }
`}</style>;
