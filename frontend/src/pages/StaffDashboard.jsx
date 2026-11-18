import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const readable = (value = '') => value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

function StaffDashboard() {
  const { user } = useAuth();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('tickets/').then((response) => {
      const data = response.data;
      setTickets(Array.isArray(data) ? data : data.results || []);
    }).catch((err) => {
      setError(err.response?.data?.detail || 'Unable to load your ticket queue.');
    }).finally(() => setLoading(false));
  }, []);

  const openCount = tickets.filter((ticket) => !['resolved', 'closed'].includes(ticket.status)).length;
  const overdueCount = tickets.filter((ticket) => ticket.is_sla_overdue).length;

  return (
    <CustomerLayout>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><p className="text-sm font-semibold uppercase tracking-wide text-blue-600">Support workspace</p><h1 className="mt-2 text-3xl font-bold text-slate-900">Ticket queue</h1><p className="mt-2 text-slate-600">Review assigned requests and keep customers updated.</p></div>
        {user?.role === 'admin' && <Link to="/admin/reports" className="rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold text-slate-700">View reports</Link>}
      </div>
      <div className="mt-7 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">Tickets in queue</p><p className="mt-2 text-3xl font-bold text-slate-900">{tickets.length}</p></div>
        <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">Active tickets</p><p className="mt-2 text-3xl font-bold text-blue-700">{openCount}</p></div>
        <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">SLA overdue</p><p className="mt-2 text-3xl font-bold text-red-600">{overdueCount}</p></div>
      </div>
      {error && <p className="mt-5 rounded-lg bg-red-50 p-4 text-red-700">{error}</p>}
      <section className="mt-7 overflow-hidden rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 p-5"><h2 className="font-semibold text-slate-900">Recent tickets</h2></div>
        {loading ? <p className="p-6 text-slate-500">Loading ticket queue...</p> : tickets.length === 0 ? <p className="p-6 text-slate-500">No tickets are currently assigned to you.</p> : <div className="overflow-x-auto"><table className="w-full min-w-[720px] text-left text-sm"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="px-5 py-3">Ticket</th><th className="px-5 py-3">Customer</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Priority</th><th className="px-5 py-3">SLA</th><th className="px-5 py-3"></th></tr></thead><tbody className="divide-y divide-slate-100">{tickets.map((ticket) => <tr key={ticket.id}><td className="px-5 py-4"><strong>{ticket.ticket_number}</strong><p className="mt-1 text-slate-500">{ticket.subject}</p></td><td className="px-5 py-4">{ticket.customer_username}</td><td className="px-5 py-4">{readable(ticket.status)}</td><td className="px-5 py-4">{readable(ticket.priority)}</td><td className={`px-5 py-4 ${ticket.is_sla_overdue ? 'font-semibold text-red-600' : 'text-slate-600'}`}>{ticket.is_sla_overdue ? 'Overdue' : ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleDateString() : '—'}</td><td className="px-5 py-4"><Link className="font-semibold text-blue-600 hover:underline" to={`/tickets/${ticket.id}`}>Open</Link></td></tr>)}</tbody></table></div>}
      </section>
    </CustomerLayout>
  );
}

export default StaffDashboard;
