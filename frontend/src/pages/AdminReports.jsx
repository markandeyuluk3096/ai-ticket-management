import { useEffect, useState } from 'react';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';

function AdminReports() {
  const [report, setReport] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('reports/dashboard/').then((response) => setReport(response.data)).catch((err) => {
      setError(err.response?.data?.detail || 'Unable to load administrator reports.');
    });
  }, []);

  return (
    <CustomerLayout>
      <h1 className="text-3xl font-bold text-slate-900">Administrator reports</h1>
      <p className="mt-2 text-slate-600">Overview of ticket volume, priorities and customer feedback.</p>
      {error && <p className="mt-5 rounded-lg bg-red-50 p-4 text-red-700">{error}</p>}
      {!report && !error && <p className="mt-8 text-slate-500">Loading reports...</p>}
      {report && <>
        <div className="mt-7 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">Total tickets</p><p className="mt-2 text-3xl font-bold text-slate-900">{report.total_tickets}</p></div>
          <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">Open</p><p className="mt-2 text-3xl font-bold text-blue-700">{report.status_counts?.open || 0}</p></div>
          <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">In progress</p><p className="mt-2 text-3xl font-bold text-amber-600">{report.status_counts?.in_progress || 0}</p></div>
          <div className="rounded-xl border border-slate-200 bg-white p-5"><p className="text-sm text-slate-500">Average rating</p><p className="mt-2 text-3xl font-bold text-emerald-700">{report.feedback?.average_rating ? Number(report.feedback.average_rating).toFixed(1) : '—'} <span className="text-sm font-medium text-slate-400">/ 5</span></p></div>
        </div>
        <div className="mt-7 grid gap-6 lg:grid-cols-2">
          <section className="rounded-xl border border-slate-200 bg-white p-6"><h2 className="font-semibold text-slate-900">Tickets by status</h2><div className="mt-4 space-y-3">{Object.entries(report.status_counts || {}).map(([status, count]) => <div key={status}><div className="flex justify-between text-sm"><span className="capitalize text-slate-600">{status.replaceAll('_', ' ')}</span><strong>{count}</strong></div><div className="mt-1 h-2 rounded-full bg-slate-100"><div className="h-2 rounded-full bg-blue-600" style={{ width: `${report.total_tickets ? (count / report.total_tickets) * 100 : 0}%` }} /></div></div>)}</div></section>
          <section className="rounded-xl border border-slate-200 bg-white p-6"><h2 className="font-semibold text-slate-900">Tickets by category</h2><div className="mt-4 space-y-3">{(report.category_counts || []).map((item) => <div key={item.category__code} className="flex justify-between gap-3 border-b border-slate-100 pb-3 text-sm"><span className="text-slate-600">{item.category__name} <span className="text-xs text-slate-400">({item.category__code})</span></span><strong>{item.total}</strong></div>)}{report.category_counts?.length === 0 && <p className="text-sm text-slate-500">No ticket data yet.</p>}</div></section>
        </div>
      </>}
    </CustomerLayout>
  );
}

export default AdminReports;
