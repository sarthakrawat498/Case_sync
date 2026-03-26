/**
 * CaseSync Main Application Component
 * Sets up routing and global layout
 */

import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import Upload from "./pages/Upload";
import Dashboard from "./pages/Dashboard";
import Review from "./pages/Review";
import useStore from "./store/useStore";

// Navigation Header Component
function Header() {
  const location = useLocation();
  const { currentCase, reset } = useStore();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="bg-police-navy text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <Link to="/" className="flex items-center space-x-3" onClick={reset}>
            <div className="w-10 h-10 bg-police-gold rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-police-navy"
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
            </div>
            <div>
              <h1 className="text-xl font-bold">CaseSync</h1>
              <p className="text-xs text-gray-300">AI-Powered FIR Generation</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-4">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive("/") ? "bg-primary-600" : "hover:bg-primary-700"
              }`}
            >
              New Case
            </Link>
            <Link
              to="/dashboard"
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive("/dashboard")
                  ? "bg-primary-600"
                  : "hover:bg-primary-700"
              }`}
            >
              Dashboard
            </Link>
            {currentCase && (
              <Link
                to={`/review/${currentCase.id}`}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname.includes("/review")
                    ? "bg-primary-600"
                    : "hover:bg-primary-700"
                }`}
              >
                Current Case
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}

// Error Boundary Component
function ErrorBoundary({ children }) {
  return children;
}

// Toast Notification Component
function ToastNotification() {
  const { error, successMessage, clearError, clearSuccess } = useStore();

  if (!error && !successMessage) return null;

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg flex items-center justify-between max-w-md">
          <div className="flex items-center">
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
            <span className="text-sm">{error}</span>
          </div>
          <button
            onClick={clearError}
            className="ml-4 text-red-500 hover:text-red-700"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      )}

      {successMessage && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-lg shadow-lg flex items-center justify-between max-w-md">
          <div className="flex items-center">
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
            <span className="text-sm">{successMessage}</span>
          </div>
          <button
            onClick={clearSuccess}
            className="ml-4 text-green-500 hover:text-green-700"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}

// Loading Overlay Component
function LoadingOverlay() {
  const loading = useStore((state) => state.loading);

  if (!loading) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl flex flex-col items-center">
        <div className="loading-spinner w-12 h-12 mb-4"></div>
        <p className="text-gray-600">Processing...</p>
      </div>
    </div>
  );
}

// Footer Component
function Footer() {
  return (
    <footer className="bg-gray-100 border-t mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <p>CaseSync - AI-Powered FIR Generation System</p>
          <p>Supports Hindi & English</p>
        </div>
      </div>
    </footer>
  );
}

// Main App Component
function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Header />
        <ToastNotification />
        <LoadingOverlay />

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Upload />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/review/:caseId" element={<Review />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
