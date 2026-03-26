/**
 * Review Page Component
 * Handles FIR review, editing, approval, and PDF download
 */

import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import useStore from "../store/useStore";
import {
  getCaseDetail,
  updateFIRDraft,
  updateCaseStatus,
  updateEntities,
  downloadPDF,
} from "../api/api";

// Status badge component
function StatusBadge({ status }) {
  const statusConfig = {
    DRAFT: { class: "badge-draft", label: "Draft", icon: "📝" },
    REVIEWED: { class: "badge-reviewed", label: "Reviewed", icon: "👀" },
    APPROVED: { class: "badge-approved", label: "Approved", icon: "✅" },
    REJECTED: { class: "badge-rejected", label: "Rejected", icon: "❌" },
  };

  const config = statusConfig[status] || statusConfig.DRAFT;

  return (
    <span className={`badge ${config.class} text-sm`}>
      {config.icon} {config.label}
    </span>
  );
}

// Language badge component
function LanguageBadge({ language }) {
  const isHindi = language === "hi";
  return (
    <span className={`badge ${isHindi ? "badge-hindi" : "badge-english"}`}>
      {isHindi ? "हिंदी (Hindi)" : "English"}
    </span>
  );
}

// Editable entity list component
function EntityList({ title, items, onUpdate, editable }) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(items.join(", "));

  const handleSave = () => {
    const newItems = editValue
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    onUpdate(newItems);
    setEditing(false);
  };

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-medium text-gray-700">{title}</h4>
        {editable && !editing && (
          <button
            onClick={() => setEditing(true)}
            className="text-xs text-primary-600 hover:text-primary-800"
          >
            Edit
          </button>
        )}
      </div>

      {editing ? (
        <div className="space-y-2">
          <input
            type="text"
            value={editValue}
            onChange={(e) => setEditValue(e.target.value)}
            className="input text-sm"
            placeholder="Comma-separated values"
          />
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              className="btn btn-primary text-xs py-1"
            >
              Save
            </button>
            <button
              onClick={() => {
                setEditing(false);
                setEditValue(items.join(", "));
              }}
              className="btn btn-secondary text-xs py-1"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap gap-1">
          {items.length > 0 ? (
            items.map((item, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs bg-gray-100 text-gray-700"
              >
                {item}
              </span>
            ))
          ) : (
            <span className="text-sm text-gray-400 italic">
              No items extracted
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function Review() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const {
    currentCase,
    transcript,
    entities,
    firDraft,
    loadFullCase,
    setFirDraft,
    setEntities,
    updateStatus,
    setLoading,
    setError,
    setSuccess,
  } = useStore();

  // Local state
  const [editingFIR, setEditingFIR] = useState(false);
  const [firContent, setFirContent] = useState("");
  const [officerNotes, setOfficerNotes] = useState("");
  const [officerName, setOfficerName] = useState("");
  const [loadingLocal, setLoadingLocal] = useState(true);

  // Load case data
  useEffect(() => {
    const loadCase = async () => {
      if (!caseId) return;

      try {
        setLoadingLocal(true);
        const fullCase = await getCaseDetail(caseId);
        loadFullCase(fullCase);

        if (fullCase.fir_draft) {
          setFirContent(fullCase.fir_draft.content);
          setOfficerNotes(fullCase.fir_draft.officer_notes || "");
        }
      } catch (error) {
        setError(error.message);
      } finally {
        setLoadingLocal(false);
      }
    };

    // Only load if we don't have the case or it's a different case
    if (!currentCase || currentCase.id !== caseId) {
      loadCase();
    } else {
      setLoadingLocal(false);
      if (firDraft) {
        setFirContent(firDraft.content);
        setOfficerNotes(firDraft.officer_notes || "");
      }
    }
  }, [caseId, currentCase, firDraft, loadFullCase, setError]);

  // Save FIR changes
  const handleSaveFIR = async () => {
    try {
      setLoading(true);
      await updateFIRDraft(caseId, {
        content: firContent,
        officer_notes: officerNotes,
      });
      setFirDraft({
        ...firDraft,
        content: firContent,
        officer_notes: officerNotes,
      });
      setEditingFIR(false);
      setSuccess("FIR draft saved successfully");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Update case status
  const handleStatusUpdate = async (newStatus) => {
    if (!officerName && newStatus !== "DRAFT") {
      setError("Please enter officer name");
      return;
    }

    try {
      setLoading(true);
      await updateCaseStatus(caseId, newStatus, officerName, officerNotes);
      updateStatus(newStatus);
      setFirDraft({ ...firDraft, status: newStatus });
      setSuccess(`Case status updated to ${newStatus}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Download PDF
  const handleDownloadPDF = async () => {
    try {
      setLoading(true);
      await downloadPDF(caseId);
      setSuccess("PDF downloaded successfully");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Update entities
  const handleEntityUpdate = async (field, values) => {
    try {
      setLoading(true);
      const updatedEntities = { [field]: values };
      await updateEntities(caseId, updatedEntities);
      setEntities({ ...entities, [field]: values });
      setSuccess("Entities updated");
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Format date safely
  const formatDate = (dateStr) => {
    if (!dateStr) return "Not available";

    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) return "Invalid date";

      return date.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (error) {
      return "Invalid date";
    }
  };

  if (loadingLocal) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner w-12 h-12"></div>
        </div>
      </div>
    );
  }

  if (!currentCase) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Case Not Found
          </h2>
          <Link to="/dashboard" className="btn btn-primary">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const isApproved = firDraft?.status === "APPROVED";
  const isReviewed = firDraft?.status === "REVIEWED";
  const isRejected = firDraft?.status === "REJECTED";

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-900">
              Case: {caseId.substring(0, 8).toUpperCase()}
            </h1>
            <StatusBadge status={firDraft?.status || "DRAFT"} />
            <LanguageBadge language={currentCase?.language} />
          </div>
          <p className="text-gray-600">
            Created: {formatDate(currentCase?.created_at)}
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link to="/dashboard" className="btn btn-secondary">
            ← Back to Dashboard
          </Link>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Transcript & Entities */}
        <div className="lg:col-span-1 space-y-6">
          {/* Transcript Box */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Transcript
            </h3>
            <div
              className={`max-h-64 overflow-y-auto p-3 bg-gray-50 rounded-lg text-sm ${
                currentCase?.language === "hi" ? "font-hindi" : ""
              }`}
            >
              {transcript?.text || "No transcript available"}
            </div>
          </div>

          {/* Entities Box */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Extracted Entities
            </h3>

            {entities ? (
              <>
                <EntityList
                  title="Person Names"
                  items={entities.person_names || []}
                  editable={!isApproved}
                  onUpdate={(values) =>
                    handleEntityUpdate("person_names", values)
                  }
                />

                <EntityList
                  title="Locations"
                  items={entities.locations || []}
                  editable={!isApproved}
                  onUpdate={(values) => handleEntityUpdate("locations", values)}
                />

                <EntityList
                  title="Dates/Times"
                  items={entities.dates || []}
                  editable={!isApproved}
                  onUpdate={(values) => handleEntityUpdate("dates", values)}
                />

                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">
                    Incident Summary
                  </h4>
                  <p
                    className={`text-sm text-gray-600 ${
                      currentCase?.language === "hi" ? "font-hindi" : ""
                    }`}
                  >
                    {entities.incident || "No incident summary extracted"}
                  </p>
                </div>
              </>
            ) : (
              <p className="text-gray-500">No entities extracted yet</p>
            )}
          </div>

          {/* Officer Input */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Officer Details
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Officer Name
                </label>
                <input
                  type="text"
                  value={officerName}
                  onChange={(e) => setOfficerName(e.target.value)}
                  disabled={isApproved}
                  className="input"
                  placeholder="Enter your name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notes
                </label>
                <textarea
                  value={officerNotes}
                  onChange={(e) => setOfficerNotes(e.target.value)}
                  disabled={isApproved}
                  className="textarea h-20"
                  placeholder="Add any notes..."
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - FIR Draft */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">FIR Draft</h3>

              {!isApproved && (
                <div className="flex items-center space-x-2">
                  {editingFIR ? (
                    <>
                      <button
                        onClick={handleSaveFIR}
                        className="btn btn-primary"
                      >
                        Save Changes
                      </button>
                      <button
                        onClick={() => {
                          setEditingFIR(false);
                          setFirContent(firDraft?.content || "");
                        }}
                        className="btn btn-secondary"
                      >
                        Cancel
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setEditingFIR(true)}
                      className="btn btn-secondary"
                    >
                      Edit FIR
                    </button>
                  )}
                </div>
              )}
            </div>

            {editingFIR ? (
              <textarea
                value={firContent}
                onChange={(e) => setFirContent(e.target.value)}
                className={`textarea h-96 font-mono text-sm ${
                  currentCase?.language === "hi" ? "font-hindi" : ""
                }`}
              />
            ) : (
              <div
                className={`fir-content h-96 overflow-y-auto ${
                  currentCase?.language === "hi" ? "font-hindi" : ""
                }`}
              >
                {firDraft?.content || "No FIR draft generated yet"}
              </div>
            )}

            {/* Action Buttons */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="flex flex-wrap items-center justify-between gap-4">
                {/* Status Actions */}
                <div className="flex items-center space-x-3">
                  {firDraft?.status === "DRAFT" && (
                    <button
                      onClick={() => handleStatusUpdate("REVIEWED")}
                      className="btn btn-secondary"
                    >
                      Mark as Reviewed
                    </button>
                  )}

                  {firDraft?.status === "REVIEWED" && (
                    <>
                      <button
                        onClick={() => handleStatusUpdate("DRAFT")}
                        className="btn btn-secondary text-yellow-600"
                      >
                        Return to Draft
                      </button>
                      <button
                        onClick={() => handleStatusUpdate("REJECTED")}
                        className="btn btn-danger"
                      >
                        Reject FIR
                      </button>
                      <button
                        onClick={() => handleStatusUpdate("APPROVED")}
                        className="btn btn-success"
                      >
                        Approve FIR
                      </button>
                    </>
                  )}

                  {firDraft?.status === "REJECTED" && (
                    <>
                      <button
                        onClick={() => handleStatusUpdate("DRAFT")}
                        className="btn btn-secondary text-yellow-600"
                      >
                        Return to Draft
                      </button>
                      <span className="text-red-600 font-medium flex items-center">
                        <svg
                          className="w-5 h-5 mr-2"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                            clipRule="evenodd"
                          />
                        </svg>
                        FIR Rejected - Needs Corrections
                      </span>
                    </>
                  )}

                  {isApproved && (
                    <span className="text-green-600 font-medium flex items-center">
                      <svg
                        className="w-5 h-5 mr-2"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                          clipRule="evenodd"
                        />
                      </svg>
                      FIR Approved
                    </span>
                  )}
                </div>

                {/* PDF Download */}
                <button
                  onClick={handleDownloadPDF}
                  className="btn btn-primary flex items-center"
                >
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  Download PDF
                </button>
              </div>
            </div>

            {/* Approval Info */}
            {(firDraft?.reviewed_by || firDraft?.approved_by) && (
              <div className="mt-4 pt-4 border-t border-gray-200 text-sm text-gray-500">
                {firDraft?.reviewed_by && (
                  <p>Reviewed by: {firDraft.reviewed_by}</p>
                )}
                {firDraft?.approved_by && (
                  <p>Approved by: {firDraft.approved_by}</p>
                )}
                {firDraft?.status === "REJECTED" && firDraft?.reviewed_by && (
                  <p className="text-red-600">
                    Rejected by: {firDraft.reviewed_by}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Review;
