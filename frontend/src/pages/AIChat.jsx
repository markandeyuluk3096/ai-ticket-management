import { useEffect, useState } from 'react';
import CustomerLayout from '../layouts/CustomerLayout';
import api from '../services/api';

function AIChat() {
  const [sessions, setSessions] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadSessions = async () => {
    try {
      const response = await api.get('ai/chat/sessions/');
      setSessions(Array.isArray(response.data) ? response.data : response.data.results || []);
    } catch {
      setError('Unable to load your previous conversations.');
    }
  };

  useEffect(() => { loadSessions(); }, []);

  const openSession = async (id) => {
    setError('');
    try {
      const response = await api.get(`ai/chat/sessions/${id}/`);
      setSessionId(id);
      setMessages(response.data.messages || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to open this conversation.');
    }
  };

  const sendMessage = async (event) => {
    event.preventDefault();
    const text = message.trim();
    if (!text || loading) return;
    setMessage('');
    setError('');
    setLoading(true);
    setMessages((current) => [...current, { id: `local-${Date.now()}`, role: 'user', content: text }]);
    try {
      const response = await api.post('ai/chat/', { message: text, ...(sessionId ? { session_id: sessionId } : {}) });
      setSessionId(response.data.session_id);
      setMessages((current) => [...current, response.data.message]);
      await loadSessions();
    } catch (err) {
      setError(err.response?.data?.detail || 'The AI assistant is unavailable. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <CustomerLayout>
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[260px_1fr]">
        <aside className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-slate-900">Your conversations</h2>
            <button onClick={() => { setSessionId(null); setMessages([]); setError(''); }} className="text-sm font-semibold text-blue-600">New</button>
          </div>
          <div className="mt-4 space-y-2">
            {sessions.map((session) => <button key={session.id} onClick={() => openSession(session.id)} className={`w-full rounded-lg p-3 text-left text-sm ${sessionId === session.id ? 'bg-blue-50 text-blue-700' : 'hover:bg-slate-50 text-slate-700'}`}>
              <span className="block truncate font-medium">{session.title}</span>
              <span className="mt-1 block text-xs text-slate-400">{new Date(session.updated_at).toLocaleDateString()}</span>
            </button>)}
            {sessions.length === 0 && <p className="text-sm text-slate-500">No conversations yet.</p>}
          </div>
        </aside>
        <section className="flex min-h-[620px] flex-col rounded-xl border border-slate-200 bg-white">
          <div className="border-b border-slate-200 p-5">
            <h1 className="text-xl font-bold text-slate-900">AI Support Assistant</h1>
            <p className="mt-1 text-sm text-slate-500">Answers are based on published FAQs. Create a ticket if you need personal support.</p>
          </div>
          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {messages.length === 0 && <div className="mx-auto mt-20 max-w-md text-center text-slate-500"><p className="text-lg font-semibold text-slate-800">How can I help?</p><p className="mt-2">Ask a question about using the service or finding support.</p></div>}
            {messages.map((item, index) => <div key={item.id || index} className={`flex ${item.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${item.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-800'}`}>{item.content}</div>
            </div>)}
            {loading && <p className="text-sm text-slate-500">Assistant is thinking...</p>}
          </div>
          {error && <p className="mx-5 mb-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <form onSubmit={sendMessage} className="flex gap-3 border-t border-slate-200 p-4">
            <input value={message} onChange={(event) => setMessage(event.target.value)} maxLength={2000} className="min-w-0 flex-1 rounded-lg border border-slate-300 px-4 py-3" placeholder="Type your question..." />
            <button disabled={loading || !message.trim()} className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white disabled:opacity-50">Send</button>
          </form>
        </section>
      </div>
    </CustomerLayout>
  );
}

export default AIChat;
