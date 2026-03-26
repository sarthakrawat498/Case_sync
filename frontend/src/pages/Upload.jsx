/**
 * Upload Page Component
 * Handles audio file upload and transcription
 */

import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import useStore from "../store/useStore";
import { uploadAudio, extractEntities, generateFIR } from "../api/api";

// Supported audio formats
const ACCEPTED_FORMATS = [
  "audio/wav",
  "audio/mpeg",
  "audio/mp3",
  "audio/mp4",
  "audio/x-m4a",
  "audio/webm",
  "audio/ogg",
];

function Upload() {
  const navigate = useNavigate();
  const {
    setCurrentCase,
    setTranscript,
    setEntities,
    setFirDraft,
    setLoading,
    setError,
    setSuccess,
    setCurrentStep,
    reset,
  } = useStore();

  // Local state
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [transcriptResult, setTranscriptResult] = useState(null);
  const [processing, setProcessing] = useState(false);

  // Handle file selection
  const handleFileSelect = useCallback(
    (selectedFile) => {
      if (!selectedFile) return;

      // Validate file type
      if (!ACCEPTED_FORMATS.includes(selectedFile.type)) {
        setError("Please upload a valid audio file (WAV, MP3, M4A, WebM, OGG)");
        return;
      }

      // Validate file size (50MB max)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError("File size must be less than 50MB");
        return;
      }

      setFile(selectedFile);
      setTranscriptResult(null);
    },
    [setError],
  );

  // Handle drag events
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  // Handle file drop
  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    },
    [handleFileSelect],
  );

  // Handle file input change
  const handleChange = useCallback(
    (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelect(e.target.files[0]);
      }
    },
    [handleFileSelect],
  );

  // Upload and process audio
  const handleUpload = async () => {
    if (!file) return;

    setProcessing(true);
    setLoading(true);
    setUploadProgress(0);

    try {
      // Step 1: Upload and transcribe
      setUploadProgress(25);
      const uploadResult = await uploadAudio(file);

      setUploadProgress(50);
      setTranscriptResult(uploadResult);

      // Store case and transcript data
      setCurrentCase({
        id: uploadResult.case_id,
        language: uploadResult.detected_language,
        status: "DRAFT",
      });

      setTranscript({
        text: uploadResult.transcript,
        audio_filename: uploadResult.audio_filename,
      });

      // Step 2: Extract entities
      setUploadProgress(75);
      const entitiesResult = await extractEntities(uploadResult.case_id);
      setEntities(entitiesResult.entities);

      // Step 3: Generate FIR
      setUploadProgress(90);
      const firResult = await generateFIR(uploadResult.case_id);
      setFirDraft({
        content: firResult.fir_content,
        status: firResult.status,
      });

      setUploadProgress(100);
      setCurrentStep(4); // Move to review step
      setSuccess("Audio processed successfully! FIR draft generated.");

      // Navigate to review page
      setTimeout(() => {
        navigate(`/review/${uploadResult.case_id}`);
      }, 1000);
    } catch (error) {
      setError(error.message);
    } finally {
      setProcessing(false);
      setLoading(false);
    }
  };

  // Clear current file
  const handleClear = () => {
    setFile(null);
    setTranscriptResult(null);
    setUploadProgress(0);
    reset();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Upload Audio Recording
        </h1>
        <p className="text-gray-600">
          Upload a complaint audio recording in Hindi or English. The system
          will automatically transcribe, extract entities, and generate an FIR
          draft.
        </p>
      </div>

      {/* Upload Area */}
      <div className="card mb-6">
        <div
          className={`upload-zone ${dragActive ? "upload-zone-active" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            id="audio-upload"
            accept={ACCEPTED_FORMATS.join(",")}
            onChange={handleChange}
            className="hidden"
          />

          {file ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center space-x-3">
                <svg
                  className="w-12 h-12 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div className="text-left">
                  <p className="font-medium text-gray-900">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-center space-x-3">
                <button
                  onClick={() =>
                    document.getElementById("audio-upload").click()
                  }
                  className="btn btn-secondary"
                >
                  Change File
                </button>
                <button
                  onClick={handleClear}
                  className="btn btn-secondary text-red-600 hover:bg-red-50"
                >
                  Remove
                </button>
              </div>
            </div>
          ) : (
            <label htmlFor="audio-upload" className="cursor-pointer">
              <div className="space-y-4">
                <svg
                  className="w-16 h-16 mx-auto text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
                <div>
                  <p className="text-lg font-medium text-gray-700">
                    Drop your audio file here
                  </p>
                  <p className="text-gray-500">
                    or{" "}
                    <span className="text-primary-600 font-medium">
                      browse files
                    </span>
                  </p>
                </div>
                <p className="text-sm text-gray-400">
                  Supported: WAV, MP3, M4A, WebM, OGG (max 50MB)
                </p>
              </div>
            </label>
          )}
        </div>

        {/* Progress Bar */}
        {processing && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">
                Processing...
              </span>
              <span className="text-sm text-gray-500">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <div className="mt-2 text-sm text-gray-500 text-center">
              {uploadProgress < 50 && "Transcribing audio..."}
              {uploadProgress >= 50 &&
                uploadProgress < 75 &&
                "Extracting entities..."}
              {uploadProgress >= 75 &&
                uploadProgress < 100 &&
                "Generating FIR draft..."}
              {uploadProgress === 100 && "Complete!"}
            </div>
          </div>
        )}

        {/* Upload Button */}
        {file && !processing && (
          <div className="mt-6 text-center">
            <button
              onClick={handleUpload}
              className="btn btn-primary px-8 py-3 text-lg"
            >
              Process Audio & Generate FIR
            </button>
          </div>
        )}
      </div>

      {/* Language Support Info */}
      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="card bg-orange-50 border-orange-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center">
              <span className="text-lg">हि</span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Hindi Support</h3>
              <p className="text-sm text-gray-600">
                Full support for Hindi audio recordings and FIR generation in
                Devanagari script
              </p>
            </div>
          </div>
        </div>

        <div className="card bg-purple-50 border-purple-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <span className="text-lg">En</span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">English Support</h3>
              <p className="text-sm text-gray-600">
                Full support for English audio recordings and formal FIR
                generation
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Info Box */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-medium text-gray-900 mb-2">How it works</h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
          <li>Upload an audio recording of the complaint (Hindi or English)</li>
          <li>AI transcribes the audio using Whisper speech recognition</li>
          <li>Named Entity Recognition extracts persons, locations, dates</li>
          <li>FIR draft is generated using the official template</li>
          <li>Review, edit, and approve the FIR</li>
          <li>Download the final FIR as PDF</li>
        </ol>
      </div>
    </div>
  );
}

export default Upload;
