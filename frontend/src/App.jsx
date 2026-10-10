import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Layout
import MainLayout from './components/layout/MainLayout';

// Auth
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import AdminLogin from './pages/AdminLogin';
import StudentRegister from './pages/StudentRegister';
import Dashboard from './pages/Dashboard';

// Pages
import StudentList from './pages/students/StudentList';
import StudentForm from './pages/students/StudentForm';
import StudentDetail from './pages/students/StudentDetail';
import FaceRegistration from './pages/students/FaceRegistration';
import StudentDashboard from './pages/students/StudentDashboard';
import MarkAttendance from './pages/students/MarkAttendance';

import SubjectList from './pages/subjects/SubjectList';
import SubjectForm from './pages/subjects/SubjectForm';

import AttendanceList from './pages/attendance/AttendanceList';
import CreateSession from './pages/attendance/CreateSession';
import SessionDetail from './pages/attendance/SessionDetail';
import LiveAttendance from './pages/attendance/LiveAttendance';

import ReportList from './pages/reports/ReportList';
import StudentReport from './pages/reports/StudentReport';
import SubjectReport from './pages/reports/SubjectReport';
import MonthlyReport from './pages/reports/MonthlyReport';

import UserList from './pages/users/UserList';
import Notifications from './pages/Notifications';
import Settings from './pages/Settings';
import AuditLogs from './pages/AuditLogs';

// Protected Route wrapper
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return children;
}

function PostLoginRedirect() {
  const { user } = useAuth();
  if (user?.role === 'student') return <Navigate to="/my-profile" replace />;
  return <Navigate to="/dashboard" replace />;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public route */}
      <Route path="/login" element={isAuthenticated ? <PostLoginRedirect /> : <Login />} />
      <Route path="/register" element={isAuthenticated ? <PostLoginRedirect /> : <StudentRegister />} />
      <Route path="/admin/login" element={isAuthenticated ? <PostLoginRedirect /> : <AdminLogin />} />

      {/* Protected routes */}
      <Route path="/" element={<ProtectedRoute><PostLoginRedirect /></ProtectedRoute>} />

      <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/my-profile" element={<StudentDashboard />} />
        <Route path="/my-profile/register-face" element={<FaceRegistration />} />
        <Route path="/my-profile/mark-attendance" element={<MarkAttendance />} />

        {/* Students */}
        <Route path="/students" element={<StudentList />} />
        <Route path="/students/add" element={<StudentForm />} />
        <Route path="/students/:id" element={<StudentDetail />} />
        <Route path="/students/:id/edit" element={<StudentForm />} />
        <Route path="/students/:id/register-face" element={<FaceRegistration />} />

        {/* Subjects */}
        <Route path="/subjects" element={<SubjectList />} />
        <Route path="/subjects/add" element={<SubjectForm />} />
        <Route path="/subjects/:id/edit" element={<SubjectForm />} />

        {/* Attendance */}
        <Route path="/attendance" element={<AttendanceList />} />
        <Route path="/attendance/session/create" element={<CreateSession />} />
        <Route path="/attendance/session/:id" element={<SessionDetail />} />
        <Route path="/attendance/live" element={<LiveAttendance />} />

        {/* Reports */}
        <Route path="/reports" element={<ReportList />} />
        <Route path="/reports/student" element={<StudentReport />} />
        <Route path="/reports/subject" element={<SubjectReport />} />
        <Route path="/reports/monthly" element={<MonthlyReport />} />

        {/* System */}
        <Route path="/users" element={<UserList />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/audit-logs" element={<AuditLogs />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;