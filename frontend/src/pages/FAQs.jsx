import { useEffect, useState } from 'react';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';

function FAQs() {
  const [query, setQuery] = useState('');
  const [faqs, setFaqs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadFaqs = async (search = '') => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get(`faqs/?search=${encodeURIComponent(search)}`);
      setFaqs(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load frequently asked questions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadFaqs(); }, []);

  return (
    <CustomerLayout>
      <div className="mx-auto max-w-4xl">
        <h1 className="text-3xl font-bold text-slate-900">Frequently Asked Questions</h1>
        <p className="mt-2 text-slate-600">Search our help articles for quick answers.</p>
        <form className="mt-6 flex gap-3" onSubmit={(event) => { event.preventDefault(); loadFaqs(query); }}>
          <input value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-4 py-3" placeholder="Search questions..." />
          <button className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700">Search</button>
        </form>
        {error && <p className="mt-5 rounded-lg bg-red-50 p-4 text-red-700">{error}</p>}
        {loading ? <p className="mt-8 text-slate-500">Loading FAQs...</p> : faqs.length === 0 ? <p className="mt-8 rounded-xl bg-white p-8 text-center text-slate-500">No published FAQs matched your search.</p> : (
          <div className="mt-6 space-y-4">
            {faqs.map((faq) => <article key={faq.id} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">{faq.category_name || 'Help article'}</p>
              <h2 className="mt-2 text-lg font-semibold text-slate-900">{faq.question}</h2>
              <p className="mt-3 whitespace-pre-wrap leading-7 text-slate-600">{faq.answer}</p>
            </article>)}
          </div>
        )}
      </div>
    </CustomerLayout>
  );
}

export default FAQs;
