import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';

function CreateTicket() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    subject: '',
    description: '',
    category_id: '',
  });
  const [loadingCategories, setLoadingCategories] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await api.get('categories/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = response.data;
        setCategories(Array.isArray(data) ? data : data.results || []);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
          'Unable to load ticket categories. Please try again.'
        );
      } finally {
        setLoadingCategories(false);
      }
    };

    loadCategories();
  }, [token]);

  const handleChange = (event) => {
    setFormData((current) => ({
      ...current,
      [event.target.name]: event.target.value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      await api.post(
        'tickets/',
        {
          subject: formData.subject.trim(),
          description: formData.description.trim(),
          category_id: Number(formData.category_id),
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      navigate('/tickets', {
        state: { message: 'Your support ticket was created successfully.' },
      });
    } catch (err) {
      const data = err.response?.data;
      const message = data
        ? Object.entries(data)
            .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`)
            .join(' | ')
        : 'Unable to connect to the server. Please try again.';
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <CustomerLayout>
      <div className="mx-auto max-w-2xl">
        <Link to="/tickets" className="text-sm font-medium text-blue-600 hover:underline">
          ← Back to My Tickets
        </Link>

        <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <h1 className="text-2xl font-bold text-slate-900">Create a Support Ticket</h1>
          <p className="mt-2 text-slate-500">Tell us what you need help with.</p>

          {error && (
            <div className="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-700" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            <div>
              <label htmlFor="subject" className="mb-2 block text-sm font-medium text-slate-700">
                Subject
              </label>
              <input
                id="subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                maxLength={200}
                required
                className="w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                placeholder="Briefly describe your issue"
              />
            </div>

            <div>
              <label htmlFor="category_id" className="mb-2 block text-sm font-medium text-slate-700">
                Category
              </label>
              <select
                id="category_id"
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                required
                disabled={loadingCategories || categories.length === 0}
                className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              >
                <option value="">
                  {loadingCategories ? 'Loading categories...' : 'Select a category'}
                </option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.name}
                  </option>
                ))}
              </select>
              {!loadingCategories && categories.length === 0 && (
                <p className="mt-2 text-sm text-amber-700">
                  No active categories are available. Please contact an administrator.
                </p>
              )}
            </div>

            <div>
              <label htmlFor="description" className="mb-2 block text-sm font-medium text-slate-700">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={6}
                required
                className="w-full resize-y rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                placeholder="Explain the issue and include any helpful details..."
              />
            </div>

            <button
              type="submit"
              disabled={submitting || loadingCategories || categories.length === 0}
              className="w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Ticket'}
            </button>
          </form>
        </div>
      </div>
    </CustomerLayout>
  );
}

export default CreateTicket;
