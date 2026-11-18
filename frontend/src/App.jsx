import { Navigate, Route, Routes } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import StaffDashboard from './pages/StaffDashboard';
import MyTickets from './pages/MyTickets';
import CreateTicket from './pages/CreateTicket';
import TicketDetail from './pages/TicketDetail';
import FAQs from './pages/FAQs';
import AIChat from './pages/AIChat';
import Notifications from './pages/Notifications';
import AdminReports from './pages/AdminReports';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';

function DashboardHome() {
  const { user } = useAuth();
  if (user?.role === 'agent' || user?.role === 'admin') return <StaffDashboard />;
  return <Dashboard />;
}

function TicketsHome() {
  const { user } = useAuth();
  if (user?.role === 'agent' || user?.role === 'admin') return <StaffDashboard />;
  return <MyTickets />;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardHome /></ProtectedRoute>} />
      <Route path="/tickets" element={<ProtectedRoute><TicketsHome /></ProtectedRoute>} />
      <Route path="/tickets/new" element={<ProtectedRoute allowedRoles={['customer']}><CreateTicket /></ProtectedRoute>} />
      <Route path="/tickets/:ticketId" element={<ProtectedRoute><TicketDetail /></ProtectedRoute>} />
      <Route path="/faqs" element={<ProtectedRoute><FAQs /></ProtectedRoute>} />
      <Route path="/chat" element={<ProtectedRoute><AIChat /></ProtectedRoute>} />
      <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      <Route path="/admin/reports" element={<ProtectedRoute allowedRoles={['admin']}><AdminReports /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
