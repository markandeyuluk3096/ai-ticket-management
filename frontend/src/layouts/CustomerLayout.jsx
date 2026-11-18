import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function CustomerLayout({ children }) {
  const { user, logout } = useAuth();
  const isStaff = user?.role === 'agent' || user?.role === 'admin';
  const isAdmin = user?.role === 'admin';
  const linkClass = ({ isActive }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition ${isActive ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`;

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4">
          <Link to="/dashboard" className="text-xl font-bold text-blue-700">AI Ticket Management</Link>
          <nav className="flex flex-wrap items-center gap-1">
            <NavLink to="/dashboard" end className={linkClass}>Dashboard</NavLink>
            <NavLink to="/tickets" className={linkClass}>{isStaff ? 'Ticket queue' : 'My Tickets'}</NavLink>
            {!isStaff && <NavLink to="/tickets/new" className={linkClass}>Create Ticket</NavLink>}
            <NavLink to="/faqs" className={linkClass}>FAQs</NavLink>
            <NavLink to="/chat" className={linkClass}>AI Assistant</NavLink>
            <NavLink to="/notifications" className={linkClass}>Notifications</NavLink>
            <NavLink to="/profile" className={linkClass}>Profile</NavLink>
            {isAdmin && <NavLink to="/admin/reports" className={linkClass}>Reports</NavLink>}
          </nav>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-slate-600 sm:inline">{user?.first_name || user?.username || 'Account'}</span>
            <button type="button" onClick={logout} className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">Logout</button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
    </div>
  );
}

export default CustomerLayout;
