/**
 * Dashboard Page Component
 * Shows all cases with filtering and navigation to review
 */

import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import useStore from "../store/useStore";
import {
  getCases,
  getDashboardStats,
  getCaseDetail,
  deleteCase,
} from "../api/api";

// Status badge component
function StatusBadge({ status }) {
  const statusClasses = {
    DRAFT: "badge-draft",
    REVIEWED: "badge-reviewed",
    APPROVED: "badge-approved",
    REJECTED: "badge-rejected",
  };

  return (
    <span className={`badge ${statusClasses[status] || "badge-draft"}`}>
      {status}
    </span>
  );
}

// Language badge component
function LanguageBadge({ language }) {
  const isHindi = language === "hi";
  return (
    <span className={`badge ${isHindi ? "badge-hindi" : "badge-english"}`}>
      {isHindi ? "Hindi" : "English"}
    </span>
  );
}

// Stats card component
function StatCard({ title, value, icon, color }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className={`text-3xl font-bold ${color}`}>{value}</p>
        </div>
        <div
          className={`w-12 h-12 rounded-full flex items-center justify-center ${color.replace("text-", "bg-").replace("600", "100")}`}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const navigate = useNavigate();
  const {
    setCases,
    setStats,
    setLoading,
    setError,
    loadFullCase,
    cases,
    totalCases,
    stats,
  } = useStore();

  // Local state
  const [statusFilter, setStatusFilter] = useState("");
  const [languageFilter, setLanguageFilter] = useState("");
  const [page, setPage] = useState(0);
  const [initialLoading, setInitialLoading] = useState(true);
  const limit = 10;

  // Load cases and stats on mount and filter change
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);

        // Load stats
        const statsData = await getDashboardStats();
        setStats(statsData);

        // Load cases with filters
        const params = {
          skip: page * limit,
          limit,
        };

        if (statusFilter) params.status = statusFilter;
        if (languageFilter) params.language = languageFilter;

        const casesData = await getCases(params);
        setCases(casesData.cases, casesData.total);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
        setInitialLoading(false);
      }
    };

    loadData();
  }, [
    statusFilter,
    languageFilter,
    page,
    setCases,
    setStats,
    setLoading,
    setError,
  ]);

  // Handle case click
  const handleCaseClick = async (caseItem) => {
    try {
      setLoading(true);
      const fullCase = await getCaseDetail(caseItem.id);
      loadFullCase(fullCase);
      navigate(`/review/${caseItem.id}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle case deletion (only for DRAFT status)
  const handleDeleteCase = async (caseItem, event) => {
    event.stopPropagation(); // Prevent navigation

    if (caseItem.status !== "DRAFT") {
      setError("Only draft cases can be deleted");
      return;
    }

    if (
      !confirm(
        `Are you sure you want to delete case ${caseItem.id.substring(0, 8).toUpperCase()}? This action cannot be undone.`,
      )
    ) {
      return;
    }

    try {
      setLoading(true);
      await deleteCase(caseItem.id);

      // Reload cases and stats
      const params = {
        skip: page * limit,
        limit,
      };
      if (statusFilter) params.status = statusFilter;
      if (languageFilter) params.language = languageFilter;

      const [casesData, statsData] = await Promise.all([
        getCases(params),
        getDashboardStats(),
      ]);

      setCases(casesData.cases, casesData.total);
      setStats(statsData);

      // Show success message
      setError(null);
      // You may want to add a success message state to the store
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Format date
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

  if (initialLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="loading-spinner w-12 h-12"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Manage and review all FIR cases</p>
        </div>
        <Link to="/" className="btn btn-primary">
          + New Case
        </Link>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
          <StatCard
            title="Total Cases"
            value={stats.total_cases}
            color="text-gray-600"
            icon={
              <svg
                className="w-6 h-6 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            }
          />
          <StatCard
            title="Draft"
            value={stats.draft_cases}
            color="text-yellow-600"
            icon={
              <svg
                className="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            }
          />
          <StatCard
            title="Reviewed"
            value={stats.reviewed_cases}
            color="text-blue-600"
            icon={
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                />
              </svg>
            }
          />
          <StatCard
            title="Approved"
            value={stats.approved_cases}
            color="text-green-600"
            icon={
              <svg
                className="w-6 h-6 text-green-600"
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
            }
          />
          <StatCard
            title="Rejected"
            value={stats.rejected_cases}
            color="text-red-600"
            icon={
              <svg
                className="w-6 h-6 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            }
          />
          <StatCard
            title="Hindi"
            value={stats.hindi_cases}
            color="text-orange-600"
            icon={<span className="text-lg font-bold text-orange-600">हि</span>}
          />
          <StatCard
            title="English"
            value={stats.english_cases}
            color="text-purple-600"
            icon={<span className="text-lg font-bold text-purple-600">En</span>}
          />
        </div>
      )}

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(0);
              }}
              className="input w-40"
            >
              <option value="">All Status</option>
              <option value="DRAFT">Draft</option>
              <option value="REVIEWED">Reviewed</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Language
            </label>
            <select
              value={languageFilter}
              onChange={(e) => {
                setLanguageFilter(e.target.value);
                setPage(0);
              }}
              className="input w-40"
            >
              <option value="">All Languages</option>
              <option value="hi">Hindi</option>
              <option value="en">English</option>
            </select>
          </div>

          <div className="ml-auto text-sm text-gray-500">
            Showing {cases.length} of {totalCases} cases
          </div>
        </div>
      </div>

      {/* Cases List */}
      <div className="card">
        {cases.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="w-16 h-16 mx-auto text-gray-300 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No cases found
            </h3>
            <p className="text-gray-500 mb-4">
              Get started by uploading an audio recording
            </p>
            <Link to="/" className="btn btn-primary">
              Upload Audio
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Case ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Language
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Updated
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {cases.map((caseItem) => (
                  <tr
                    key={caseItem.id}
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => handleCaseClick(caseItem)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="font-mono text-sm text-gray-900">
                        {caseItem.id.substring(0, 8).toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <LanguageBadge language={caseItem.language} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={caseItem.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(caseItem.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(caseItem.updated_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          className="text-primary-600 hover:text-primary-900 font-medium"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCaseClick(caseItem);
                          }}
                        >
                          View →
                        </button>
                        {caseItem.status === "DRAFT" && (
                          <button
                            className="text-red-600 hover:text-red-900 font-medium ml-2"
                            onClick={(e) => handleDeleteCase(caseItem, e)}
                            title="Delete draft case"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalCases > limit && (
          <div className="flex items-center justify-between border-t border-gray-200 px-6 py-3">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="btn btn-secondary disabled:opacity-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-500">
              Page {page + 1} of {Math.ceil(totalCases / limit)}
            </span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * limit >= totalCases}
              className="btn btn-secondary disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
