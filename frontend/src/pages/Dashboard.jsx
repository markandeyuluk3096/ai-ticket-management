
import { useAuth } from '../context/AuthContext';

function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-100 p-8">
      <h1 className="text-3xl font-bold text-blue-600">
        AI Ticket Management
      </h1>

      <div className="mt-8 bg-white rounded-xl shadow p-6">
        <h2 className="text-2xl font-semibold">
          Welcome, {user?.first_name || user?.username || 'Customer'}!
        </h2>

        <p className="text-gray-500 mt-2">
          Manage your support tickets from here.
        </p>

        <p className="mt-4 text-gray-700">
          Email: {user?.email}
        </p>

        <button
          onClick={logout}
          className="mt-6 bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700"
        >
          Logout
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
