import { useEffect, useState } from 'react';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';

function Notifications() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    try {
      const response = await api.get('notifications/');
      setItems(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const markRead = async (id) => {
    try {
      await api.patch(`notifications/${id}/read/`, {});
      setItems((current) => current.map((item) => item.id === id ? { ...item, is_read: true } : item));
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to update this notification.');
    }
  };

  return (
    <CustomerLayout>
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold text-slate-900">Notifications</h1>
        <p className="mt-2 text-slate-600">Updates about your support requests.</p>
        {error && <p className="mt-5 rounded-lg bg-red-50 p-4 text-red-700">{error}</p>}
        {loading ? <p className="mt-8 text-slate-500">Loading notifications...</p> : items.length === 0 ? <p className="mt-8 rounded-xl bg-white p-8 text-center text-slate-500">You're all caught up. No notifications yet.</p> : (
          <div className="mt-6 space-y-3">
            {items.map((item) => <article key={item.id} className={`rounded-xl border p-5 ${item.is_read ? 'border-slate-200 bg-white' : 'border-blue-200 bg-blue-50'}`}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div><h2 className="font-semibold text-slate-900">{item.title}</h2><p className="mt-2 text-sm leading-6 text-slate-600">{item.message}</p><p className="mt-3 text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</p></div>
                {!item.is_read && <button onClick={() => markRead(item.id)} className="text-sm font-semibold text-blue-700 hover:underline">Mark as read</button>}
              </div>
            </article>)}
          </div>
        )}
      </div>
    </CustomerLayout>
  );
}

export default Notifications;
