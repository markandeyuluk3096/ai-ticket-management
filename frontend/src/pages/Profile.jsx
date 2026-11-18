import { useEffect, useState } from 'react';
import CustomerLayout from '../layouts/CustomerLayout';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

function Profile() {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone_number: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    api.get('accounts/profile/').then((response) => {
      setForm({
        first_name: response.data.first_name || '',
        last_name: response.data.last_name || '',
        email: response.data.email || '',
        phone_number: response.data.phone_number || '',
      });
    }).catch((err) => {
      setError(err.response?.data?.detail || 'Unable to load your profile.');
    }).finally(() => setLoading(false));
  }, []);

  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));

  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const response = await api.patch('accounts/profile/', form);
      updateUser(response.data);
      setSuccess('Your profile has been updated.');
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(' ') : 'Unable to save your profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <CustomerLayout>
      <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-bold text-slate-900">My profile</h1>
        <p className="mt-2 text-slate-600">Manage the contact details on your support account.</p>
        {error && <p className="mt-5 rounded-lg bg-red-50 p-4 text-red-700" role="alert">{error}</p>}
        {success && <p className="mt-5 rounded-lg bg-green-50 p-4 text-green-700" role="status">{success}</p>}
        <form onSubmit={save} className="mt-6 space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          {loading ? <p className="text-slate-500">Loading profile...</p> : <>
            <div><label className="mb-2 block text-sm font-medium text-slate-700">Username</label><input value={user?.username || ''} readOnly className="w-full rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-slate-500" /></div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div><label className="mb-2 block text-sm font-medium text-slate-700">First name</label><input name="first_name" value={form.first_name} onChange={change} className="w-full rounded-lg border border-slate-300 px-4 py-3" /></div>
              <div><label className="mb-2 block text-sm font-medium text-slate-700">Last name</label><input name="last_name" value={form.last_name} onChange={change} className="w-full rounded-lg border border-slate-300 px-4 py-3" /></div>
            </div>
            <div><label className="mb-2 block text-sm font-medium text-slate-700">Email</label><input type="email" name="email" value={form.email} onChange={change} required className="w-full rounded-lg border border-slate-300 px-4 py-3" /></div>
            <div><label className="mb-2 block text-sm font-medium text-slate-700">Phone number</label><input type="tel" name="phone_number" value={form.phone_number} onChange={change} className="w-full rounded-lg border border-slate-300 px-4 py-3" /></div>
            <p className="text-xs text-slate-500">Account role: {user?.role || 'customer'}</p>
            <button disabled={saving} className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white disabled:opacity-50">{saving ? 'Saving...' : 'Save profile'}</button>
          </>}
        </form>
      </div>
    </CustomerLayout>
  );
}

export default Profile;
