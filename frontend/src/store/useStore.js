/**
 * CaseSync Global State Store
 * Uses Zustand for lightweight state management
 */

import { create } from "zustand";

const useStore = create((set, get) => ({
  // ============== Current Case State ==============
  currentCase: null,
  transcript: null,
  entities: null,
  firDraft: null,

  // ============== UI State ==============
  loading: false,
  error: null,
  successMessage: null,

  // ============== Case List State ==============
  cases: [],
  totalCases: 0,
  stats: null,

  // ============== Current Step Tracking ==============
  currentStep: 1, // 1: Upload, 2: Entities, 3: FIR, 4: Review, 5: PDF

  // ============== Actions ==============

  /**
   * Set current case data
   * @param {Object} caseData - Case object with id, language, status
   */
  setCurrentCase: (caseData) =>
    set({
      currentCase: caseData,
      error: null,
    }),

  /**
   * Set transcript data
   * @param {Object} transcriptData - Transcript object
   */
  setTranscript: (transcriptData) =>
    set({
      transcript: transcriptData,
      error: null,
    }),

  /**
   * Set extracted entities
   * @param {Object} entitiesData - Entities object
   */
  setEntities: (entitiesData) =>
    set({
      entities: entitiesData,
      error: null,
    }),

  /**
   * Set FIR draft
   * @param {Object} firData - FIR draft object
   */
  setFirDraft: (firData) =>
    set({
      firDraft: firData,
      error: null,
    }),

  /**
   * Update case status
   * @param {string} status - New status
   */
  updateStatus: (status) =>
    set((state) => ({
      currentCase: state.currentCase ? { ...state.currentCase, status } : null,
      firDraft: state.firDraft ? { ...state.firDraft, status } : null,
    })),

  /**
   * Set cases list
   * @param {Array} cases - Array of case objects
   * @param {number} total - Total count
   */
  setCases: (cases, total) =>
    set({
      cases,
      totalCases: total,
    }),

  /**
   * Set dashboard stats
   * @param {Object} stats - Stats object
   */
  setStats: (stats) => set({ stats }),

  /**
   * Set loading state
   * @param {boolean} loading - Loading state
   */
  setLoading: (loading) => set({ loading }),

  /**
   * Set error message
   * @param {string} error - Error message
   */
  setError: (error) =>
    set({
      error,
      loading: false,
    }),

  /**
   * Clear error
   */
  clearError: () => set({ error: null }),

  /**
   * Set success message
   * @param {string} message - Success message
   */
  setSuccess: (message) =>
    set({
      successMessage: message,
      error: null,
    }),

  /**
   * Clear success message
   */
  clearSuccess: () => set({ successMessage: null }),

  /**
   * Set current workflow step
   * @param {number} step - Step number (1-5)
   */
  setCurrentStep: (step) => set({ currentStep: step }),

  /**
   * Load full case data from API response
   * @param {Object} fullCaseData - Complete case detail response
   */
  loadFullCase: (fullCaseData) =>
    set({
      currentCase: fullCaseData.case,
      transcript: fullCaseData.transcript,
      entities: fullCaseData.entities,
      firDraft: fullCaseData.fir_draft,
      error: null,
      // Determine current step based on available data
      currentStep: fullCaseData.fir_draft
        ? 4
        : fullCaseData.entities
          ? 3
          : fullCaseData.transcript
            ? 2
            : 1,
    }),

  /**
   * Reset all state (for new case)
   */
  reset: () =>
    set({
      currentCase: null,
      transcript: null,
      entities: null,
      firDraft: null,
      loading: false,
      error: null,
      successMessage: null,
      currentStep: 1,
    }),

  /**
   * Check if current case can proceed to next step
   * @returns {boolean}
   */
  canProceed: () => {
    const state = get();
    switch (state.currentStep) {
      case 1:
        return !!state.transcript;
      case 2:
        return !!state.entities;
      case 3:
        return !!state.firDraft;
      case 4:
        return state.firDraft?.status === "APPROVED";
      default:
        return false;
    }
  },

  /**
   * Get language display name
   * @returns {string}
   */
  getLanguageDisplay: () => {
    const state = get();
    if (!state.currentCase) return "";
    return state.currentCase.language === "hi" ? "Hindi" : "English";
  },

  /**
   * Check if case is approved
   * @returns {boolean}
   */
  isApproved: () => {
    const state = get();
    return state.firDraft?.status === "APPROVED";
  },
}));

export default useStore;
