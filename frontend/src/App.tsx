import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import { ProtectedRoute } from './components/ProtectedRoute';
import ResumeHistory from './pages/ResumeHistory';
import Companies from './pages/Companies';
import CompanyDetails from './pages/CompanyDetails';
import Analysis from './pages/Analysis';
import AnalysisDashboard from './pages/AnalysisDashboard';
import LearningRoadmap from './pages/LearningRoadmap';
import AnalysisHistory from './pages/AnalysisHistory';
import ResumeGrammarChecker from './pages/ResumeGrammarChecker';
import Navbar from './components/Navbar';
import LearningSetup from './pages/LearningSetup';
import LearningDashboard from './pages/LearningDashboard';
import MockTest from './pages/MockTest';
import { Toaster } from 'react-hot-toast';
import SkillAssessment from './pages/SkillAssessment';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Dashboard />
                </>
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/history" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <AnalysisHistory />
                </>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/resume-history" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <ResumeHistory />
                </>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/companies" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Companies />
                </>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/company/:companyName" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <CompanyDetails />
                </>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/analysis" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <Analysis />
                </>
              </ProtectedRoute>
            } 
          />

          <Route
            path="/resume-grammar"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <ResumeGrammarChecker />
                </>
              </ProtectedRoute>
            }
          />

          <Route 
            path="/analysis/:id" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <AnalysisDashboard />
                </>
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/roadmap/:id" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <LearningRoadmap />
                </>
              </ProtectedRoute>
            } 
          />

          <Route path="/learning/setup" element={<ProtectedRoute><><Navbar /><LearningSetup /></></ProtectedRoute>} />
          <Route path="/learning/:id" element={<ProtectedRoute><><Navbar /><LearningDashboard /></></ProtectedRoute>} />
          <Route path="/learning/:id/test/:skill" element={<ProtectedRoute><><Navbar /><MockTest /></></ProtectedRoute>} />
          <Route path="/skill-assessment" element={<ProtectedRoute><><Navbar /><SkillAssessment /></></ProtectedRoute>} />

          <Route 
            path="/analysis-history" 
            element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <AnalysisHistory />
                </>
              </ProtectedRoute>
            } 
          />

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
