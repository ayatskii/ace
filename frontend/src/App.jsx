import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';

// Auth
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';

// Student
import StudentDashboard from './pages/student/Dashboard';
import TestList from './pages/student/TestList';
import TestDetail from './pages/student/TestDetail';
import TestAttempt from './pages/student/TestAttempt';
import Profile from './pages/student/Profile';
import Results from './pages/student/Results';

// Teacher
import TeacherDashboard from './pages/teacher/Dashboard';
import GradeWriting from './pages/teacher/GradeWriting';
import GradeSpeaking from './pages/teacher/GradeSpeaking';
import TeacherHistory from './pages/teacher/TeacherHistory';

// Admin
import AdminDashboard from './pages/admin/Dashboard';
import UserManagement from './pages/admin/UserManagement';
import TestManagement from './pages/admin/TestManagement';
import CreateTest from './pages/admin/CreateTest';
import TestEditor from './pages/admin/TestEditor';
import MediaLibrary from './pages/admin/MediaLibrary';
import Settings from './pages/admin/Settings';

// Routes
import ProtectedRoute from './routes/ProtectedRoute';
import RoleRoute from './routes/RoleRoute';
import { UserRole } from './utils/constants';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const loadUser = useAuthStore((state) => state.loadUser);
  
  useEffect(() => {
    loadUser();
  }, [loadUser]);
  
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          
          {/* Student routes */}
          <Route path="/student/dashboard" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.STUDENT]}><StudentDashboard /></RoleRoute></ProtectedRoute>} />
          <Route path="/student/tests" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.STUDENT]}><TestList /></RoleRoute></ProtectedRoute>} />
          <Route path="/student/tests/:id" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.STUDENT]}><TestDetail /></RoleRoute></ProtectedRoute>} />
          <Route path="/student/test/:attemptId" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.STUDENT]}><TestAttempt /></RoleRoute></ProtectedRoute>} />
          <Route path="/student/results" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.STUDENT]}><Results /></RoleRoute></ProtectedRoute>} />
          <Route path="/student/profile" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.STUDENT]}><Profile /></RoleRoute></ProtectedRoute>} />
          
          {/* Teacher routes */}
          <Route path="/teacher/dashboard" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}><TeacherDashboard /></RoleRoute></ProtectedRoute>} />
          <Route path="/teacher/grading/writing" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}><GradeWriting /></RoleRoute></ProtectedRoute>} />
          <Route path="/teacher/grading/writing" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}><GradeWriting /></RoleRoute></ProtectedRoute>} />
          <Route path="/teacher/grading/speaking" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}><GradeSpeaking /></RoleRoute></ProtectedRoute>} />
          <Route path="/teacher/history" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.TEACHER, UserRole.ADMIN]}><TeacherHistory /></RoleRoute></ProtectedRoute>} />
          
          {/* Admin routes */}
          <Route path="/admin/dashboard" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><AdminDashboard /></RoleRoute></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><UserManagement /></RoleRoute></ProtectedRoute>} />
          <Route path="/admin/tests" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><TestManagement /></RoleRoute></ProtectedRoute>} />
          <Route path="/admin/tests/create" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><CreateTest /></RoleRoute></ProtectedRoute>} />
          <Route path="/admin/tests/:testId/edit" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><TestEditor /></RoleRoute></ProtectedRoute>} />
          <Route path="/admin/media" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><MediaLibrary /></RoleRoute></ProtectedRoute>} />
          <Route path="/admin/settings" element={<ProtectedRoute><RoleRoute allowedRoles={[UserRole.ADMIN]}><Settings /></RoleRoute></ProtectedRoute>} />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
