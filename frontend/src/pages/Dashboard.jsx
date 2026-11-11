import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CustomerLayout from '../layouts/CustomerLayout';

function Dashboard() {
  const { user } = useAuth();

  return (
    <CustomerLayout>
      <section className="rounded-2xl bg-gradient-to-r from-blue-700 to-indigo-700 p-8 text-white shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wider text-blue-100">
          Customer Dashboard
        </p>
        <h1 className="mt-3 text-3xl font-bold">
          Welcome, {user?.first_name || user?.username || 'Customer'}!
        </h1>
        <p className="mt-3 max-w-2xl text-blue-100">
          Create a support request and keep track of updates from your support team.
        </p>
        <Link
          to="/tickets/new"
          className="mt-6 inline-flex rounded-lg bg-white px-5 py-3 font-semibold text-blue-700 hover:bg-blue-50"
        >
          Create a Ticket
        </Link>
      </section>

      <div className="mt-8 grid gap-5 sm:grid-cols-2">
        <Link
          to="/tickets"
          className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
        >
          <div className="text-sm font-semibold text-blue-600">SUPPORT REQUESTS</div>
          <h2 className="mt-3 text-xl font-bold text-slate-900">My Tickets</h2>
          <p className="mt-2 text-slate-500">View your submitted tickets and check their current status.</p>
          <span className="mt-5 inline-block font-semibold text-blue-600">View tickets →</span>
        </Link>

        <Link
          to="/tickets/new"
          className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md"
        >
          <div className="text-sm font-semibold text-emerald-600">NEED HELP?</div>
          <h2 className="mt-3 text-xl font-bold text-slate-900">Create a Ticket</h2>
          <p className="mt-2 text-slate-500">Describe an issue and send it to the support team.</p>
          <span className="mt-5 inline-block font-semibold text-blue-600">Get started →</span>
        </Link>
      </div>
    </CustomerLayout>
  );
}

export default Dashboard;
