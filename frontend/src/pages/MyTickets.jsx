import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';

const statusStyles = {
  open: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-amber-100 text-amber-700',
  waiting: 'bg-purple-100 text-purple-700',
  resolved: 'bg-green-100 text-green-700',
  closed: 'bg-slate-200 text-slate-700',
};

const readable = (value = '') =>
  value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

function MyTickets() {
  const location = useLocation();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState(location.state?.message || '');

  useEffect(() => {
    const loadTickets = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await api.get('tickets/');
        const data = response.data;
        setTickets(Array.isArray(data) ? data : data.results || []);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
          'We could not load your tickets. Please try again.'
        );
      } finally {
        setLoading(false);
      }
    };

    loadTickets();
  }, []);

  return (
    <CustomerLayout>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">My Tickets</h1>
          <p className="mt-2 text-slate-500">View and track your support requests.</p>
        </div>
        <Link
          to="/tickets/new"
          className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
        >
          + Create Ticket
        </Link>
      </div>

      {message && (
        <div className="mt-6 rounded-lg bg-green-50 p-4 text-green-700" role="status">
          {message}
          <button
            type="button"
            onClick={() => setMessage('')}
            className="ml-3 font-semibold underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-700" role="alert">
          {error}
        </div>
      )}

      <section className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {loading ? (
          <p className="p-8 text-center text-slate-500">Loading your tickets...</p>
        ) : tickets.length === 0 ? (
          <div className="p-10 text-center">
            <h2 className="text-xl font-semibold text-slate-800">No tickets yet</h2>
            <p className="mt-2 text-slate-500">Create a support ticket and it will appear here.</p>
            <Link
              to="/tickets/new"
              className="mt-5 inline-block rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700"
            >
              Create your first ticket
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-6 py-4">Ticket</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Priority</th>
                  <th className="px-6 py-4">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {tickets.map((ticket) => (
                  <tr key={ticket.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <p className="font-semibold text-slate-800">{ticket.subject}</p>
                      <p className="mt-1 text-xs text-slate-500">{ticket.ticket_number}</p>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{ticket.category_name || '—'}</td>
                    <td className="px-6 py-4">
                      <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[ticket.status] || 'bg-slate-100 text-slate-700'}`}>
                        {readable(ticket.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">{readable(ticket.priority)}</td>
                    <td className="px-6 py-4 text-slate-600">
                      {ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </CustomerLayout>
  );
}

export default MyTickets;
