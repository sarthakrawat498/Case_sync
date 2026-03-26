/**
 * CaseSync API Client
 * Handles all API communication with the FastAPI backend
 */

import axios from "axios";

// Create axios instance with base configuration
const api = axios.create({
  baseURL: "/api", // Proxied to backend in development
  timeout: 60000, // 60 second timeout for audio processing
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error("[API] Request error:", error);
    return Promise.reject(error);
  },
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error(
      "[API] Response error:",
      error.response?.data || error.message,
    );

    // Extract error message
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";

    return Promise.reject(new Error(message));
  },
);

// ============== Audio Upload APIs ==============

/**
 * Upload audio file for transcription
 * @param {File} file - Audio file to upload
 * @returns {Promise} Response with case_id, transcript, and detected_language
 */
export const uploadAudio = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload/audio", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

/**
 * Get transcript for a case
 * @param {string} caseId - Case UUID
 * @returns {Promise} Transcript data
 */
export const getTranscript = async (caseId) => {
  const response = await api.get(`/upload/transcript/${caseId}`);
  return response.data;
};

/**
 * Update transcript text
 * @param {string} caseId - Case UUID
 * @param {string} text - New transcript text
 * @returns {Promise} Updated transcript
 */
export const updateTranscript = async (caseId, text) => {
  const formData = new FormData();
  formData.append("text", text);

  const response = await api.put(`/upload/transcript/${caseId}`, formData);
  return response.data;
};

// ============== NER (Entity Extraction) APIs ==============

/**
 * Extract entities from transcript
 * @param {string} caseId - Case UUID
 * @returns {Promise} Extracted entities
 */
export const extractEntities = async (caseId) => {
  const response = await api.post(`/ner/extract/${caseId}`);
  return response.data;
};

/**
 * Get extracted entities for a case
 * @param {string} caseId - Case UUID
 * @returns {Promise} Entity data
 */
export const getEntities = async (caseId) => {
  const response = await api.get(`/ner/entities/${caseId}`);
  return response.data;
};

/**
 * Update extracted entities
 * @param {string} caseId - Case UUID
 * @param {Object} entities - Updated entity values
 * @returns {Promise} Updated entities
 */
export const updateEntities = async (caseId, entities) => {
  const response = await api.put(`/ner/entities/${caseId}`, entities);
  return response.data;
};

// ============== FIR Generation APIs ==============

/**
 * Generate FIR draft from entities
 * @param {string} caseId - Case UUID
 * @param {Object} options - Optional generation parameters
 * @returns {Promise} Generated FIR draft
 */
export const generateFIR = async (caseId, options = {}) => {
  const response = await api.post(`/fir/generate/${caseId}`, options);
  return response.data;
};

/**
 * Get FIR draft for a case
 * @param {string} caseId - Case UUID
 * @returns {Promise} FIR draft data
 */
export const getFIRDraft = async (caseId) => {
  const response = await api.get(`/fir/draft/${caseId}`);
  return response.data;
};

/**
 * Update FIR draft content
 * @param {string} caseId - Case UUID
 * @param {Object} data - { content, officer_notes }
 * @returns {Promise} Updated FIR draft
 */
export const updateFIRDraft = async (caseId, data) => {
  const response = await api.put(`/fir/draft/${caseId}`, data);
  return response.data;
};

// ============== Review APIs ==============

/**
 * Update case status
 * @param {string} caseId - Case UUID
 * @param {string} status - New status (DRAFT, REVIEWED, APPROVED)
 * @param {string} officerName - Optional officer name
 * @param {string} notes - Optional notes
 * @returns {Promise} Status update response
 */
export const updateCaseStatus = async (
  caseId,
  status,
  officerName = null,
  notes = null,
) => {
  const response = await api.put(`/review/status/${caseId}`, {
    status,
    officer_name: officerName,
    notes,
  });
  return response.data;
};

/**
 * Get list of all cases
 * @param {Object} params - Filter parameters { status, language, skip, limit }
 * @returns {Promise} Case list with total count
 */
export const getCases = async (params = {}) => {
  const response = await api.get("/review/cases", { params });
  return response.data;
};

/**
 * Get complete case details
 * @param {string} caseId - Case UUID
 * @returns {Promise} Full case details including transcript, entities, FIR
 */
export const getCaseDetail = async (caseId) => {
  const response = await api.get(`/review/case/${caseId}`);
  return response.data;
};

/**
 * Get dashboard statistics
 * @returns {Promise} Stats object
 */
export const getDashboardStats = async () => {
  const response = await api.get("/review/stats");
  return response.data;
};

/**
 * Delete a case (only DRAFT status)
 * @param {string} caseId - Case UUID
 * @returns {Promise} Delete confirmation
 */
export const deleteCase = async (caseId) => {
  const response = await api.delete(`/review/case/${caseId}`);
  return response.data;
};

// ============== PDF APIs ==============

/**
 * Generate and download PDF
 * @param {string} caseId - Case UUID
 * @returns {Promise} PDF blob for download
 */
export const downloadPDF = async (caseId) => {
  const response = await api.get(`/pdf/generate/${caseId}`, {
    responseType: "blob",
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;

  // Extract filename from Content-Disposition header or use default
  const contentDisposition = response.headers["content-disposition"];
  let filename = `FIR_${caseId.substring(0, 8)}.pdf`;

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename=(.+)/);
    if (filenameMatch) {
      filename = filenameMatch[1].replace(/"/g, "");
    }
  }

  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);

  return { success: true, filename };
};

/**
 * Check PDF preview info
 * @param {string} caseId - Case UUID
 * @returns {Promise} PDF info
 */
export const getPDFPreview = async (caseId) => {
  const response = await api.get(`/pdf/preview/${caseId}`);
  return response.data;
};

// Export API instance for custom requests
export default api;
