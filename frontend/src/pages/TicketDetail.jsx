import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import CustomerLayout from '../layouts/CustomerLayout';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const statuses = ['open', 'in_progress', 'waiting', 'resolved', 'closed'];
const priorities = ['low', 'medium', 'high', 'urgent'];
const label = (value = '') => value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());

function TicketDetail() {
  const { ticketId } = useParams();
  const { user } = useAuth();
  const [ticket, setTicket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [body, setBody] = useState('');
  const [attachment, setAttachment] = useState(null);
  const [status, setStatus] = useState('');
  const [priority, setPriority] = useState('');
  const [agents, setAgents] = useState([]);
  const [assignedAgent, setAssignedAgent] = useState('');
  const [rating, setRating] = useState('5');
  const [comment, setComment] = useState('');
  const [feedbackSent, setFeedbackSent] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const requests = [api.get(`tickets/${ticketId}/`), api.get(`tickets/${ticketId}/messages/`)];
      if (user?.role === 'admin') requests.push(api.get('accounts/agents/'));
      const [ticketResponse, messageResponse, agentsResponse] = await Promise.all(requests);
      setTicket(ticketResponse.data);
      setStatus(ticketResponse.data.status);
      setPriority(ticketResponse.data.priority);
      setAssignedAgent(ticketResponse.data.assigned_agent ? String(ticketResponse.data.assigned_agent) : '');
      if (agentsResponse) setAgents(agentsResponse.data);
      const data = messageResponse.data;
      setMessages(Array.isArray(data) ? data : data.results || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to load this ticket. Check your access and try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [ticketId, user?.role]);

  const sendReply = async (event) => {
    event.preventDefault();
    if (!body.trim() && !attachment) return;
    try {
      const payload = new FormData();
      if (body.trim()) payload.append('body', body.trim());
      if (attachment) payload.append('attachment', attachment);
      const response = await api.post(`tickets/${ticketId}/messages/`, payload, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessages((current) => [...current, response.data]);
      setBody('');
      setAttachment(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to send your reply.');
    }
  };

  const saveChanges = async (event) => {
    event.preventDefault();
    try {
      await api.patch(`tickets/${ticketId}/`, {
        status,
        priority,
        ...(user?.role === 'admin' ? { assigned_agent: assignedAgent || null } : {}),
      });
      const refreshed = await api.get(`tickets/${ticketId}/`);
      setTicket(refreshed.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to update this ticket.');
    }
  };

  const runAnalysis = async () => {
    setAnalysisLoading(true);
    setError('');
    try {
      const response = await api.post(`ai/tickets/${ticketId}/analyze/`);
      setAnalysis(response.data.result);
    } catch (err) {
      setError(err.response?.data?.detail || 'AI analysis is unavailable. Check the OpenAI API configuration.');
    } finally {
      setAnalysisLoading(false);
    }
  };

  const submitFeedback = async (event) => {
    event.preventDefault();
    try {
      await api.post(`feedback/tickets/${ticketId}/`, { rating: Number(rating), comment });
      setFeedbackSent(true);
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat().join(' ') : 'Unable to submit feedback.');
    }
  };

  if (loading) return <CustomerLayout><p className="text-slate-500">Loading ticket...</p></CustomerLayout>;
  if (error && !ticket) return <CustomerLayout><p className="rounded-lg bg-red-50 p-4 text-red-700">{error}</p><Link to="/tickets" className="mt-4 inline-block text-blue-600">Back to tickets</Link></CustomerLayout>;
  if (!ticket) return null;

  const isStaff = user?.role === 'agent' || user?.role === 'admin';
  const canFeedback = user?.role === 'customer' && ['resolved', 'closed'].includes(ticket.status);

  return (
    <CustomerLayout>
      <div className="mx-auto max-w-4xl">
        <Link to="/tickets" className="text-sm font-medium text-blue-600 hover:underline">← Back to tickets</Link>
        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div><p className="text-xs font-semibold uppercase tracking-wide text-blue-600">{ticket.ticket_number}</p><h1 className="mt-2 text-2xl font-bold text-slate-900">{ticket.subject}</h1><p className="mt-2 text-sm text-slate-500">{ticket.category_name} · Created {new Date(ticket.created_at).toLocaleString()}</p></div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">{label(ticket.status)}</span>
          </div>
          <p className="mt-6 whitespace-pre-wrap leading-7 text-slate-700">{ticket.description}</p>
          <div className="mt-5 grid gap-3 text-sm sm:grid-cols-3">
            <p><span className="text-slate-500">Priority:</span> <strong>{label(ticket.priority)}</strong></p>
            <p><span className="text-slate-500">Assigned to:</span> <strong>{ticket.assigned_agent_username || 'Unassigned'}</strong></p>
            <p><span className="text-slate-500">SLA due:</span> <strong>{ticket.sla_due_at ? new Date(ticket.sla_due_at).toLocaleString() : '—'}</strong></p>
          </div>
        </div>

        {isStaff && <section className="mt-5 rounded-xl border border-slate-200 bg-white p-5">
          <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="font-semibold text-slate-900">AI ticket analysis</h2><p className="mt-1 text-sm text-slate-500">Generate a triage suggestion for the support team.</p></div><button type="button" onClick={runAnalysis} disabled={analysisLoading} className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white disabled:opacity-50">{analysisLoading ? 'Analyzing...' : 'Analyze ticket'}</button></div>
          {analysis && <div className="mt-4 grid gap-3 sm:grid-cols-2"><p className="rounded-lg bg-slate-50 p-3 text-sm"><strong>Suggested category:</strong> {analysis.category || 'Not determined'}</p><p className="rounded-lg bg-slate-50 p-3 text-sm"><strong>Suggested priority:</strong> {label(analysis.priority)}</p><p className="rounded-lg bg-slate-50 p-3 text-sm"><strong>Sentiment:</strong> {label(analysis.sentiment)}</p><p className="rounded-lg bg-slate-50 p-3 text-sm sm:col-span-2"><strong>Summary:</strong> {analysis.summary}</p><p className="rounded-lg bg-blue-50 p-3 text-sm text-blue-900 sm:col-span-2"><strong>Suggested reply (review before sending):</strong><br />{analysis.suggested_response}</p></div>}
        </section>}

        {isStaff && <form onSubmit={saveChanges} className="mt-5 flex flex-wrap items-end gap-4 rounded-xl border border-slate-200 bg-white p-5">
          <label className="text-sm font-medium text-slate-700">Status<select value={status} onChange={(event) => setStatus(event.target.value)} className="mt-2 block rounded-lg border border-slate-300 px-3 py-2">{statuses.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select></label>
          <label className="text-sm font-medium text-slate-700">Priority<select value={priority} onChange={(event) => setPriority(event.target.value)} className="mt-2 block rounded-lg border border-slate-300 px-3 py-2">{priorities.map((value) => <option key={value} value={value}>{label(value)}</option>)}</select></label>
          {user?.role === 'admin' && <label className="text-sm font-medium text-slate-700">Assign agent<select value={assignedAgent} onChange={(event) => setAssignedAgent(event.target.value)} className="mt-2 block rounded-lg border border-slate-300 px-3 py-2"><option value="">Unassigned</option>{agents.map((agent) => <option key={agent.id} value={agent.id}>{agent.first_name || agent.username} (@{agent.username})</option>)}</select></label>}
          <button className="rounded-lg bg-blue-600 px-5 py-2.5 font-semibold text-white">Save changes</button>
        </form>}

        {error && <p className="mt-4 rounded-lg bg-red-50 p-4 text-red-700">{error}</p>}

        <section className="mt-5 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-900">Conversation</h2>
          <div className="mt-5 space-y-4">
            {messages.map((item) => <article key={item.id} className="rounded-lg bg-slate-50 p-4">
              <div className="flex flex-wrap justify-between gap-2"><strong className="text-sm text-slate-800">{item.sender_username || 'Support'}</strong><span className="text-xs text-slate-400">{new Date(item.created_at).toLocaleString()}</span></div>
              {item.body && <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{item.body}</p>}
              {item.attachment && <a href={item.attachment} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sm font-semibold text-blue-600 hover:underline">View attachment</a>}
            </article>)}
            {messages.length === 0 && <p className="text-sm text-slate-500">No replies yet. Send the first message below.</p>}
          </div>
          <form onSubmit={sendReply} className="mt-5 space-y-3">
            <textarea value={body} onChange={(event) => setBody(event.target.value)} rows={3} maxLength={5000} className="w-full rounded-lg border border-slate-300 p-3" placeholder="Write a reply..." />
            <div className="flex flex-wrap items-center justify-between gap-3"><label className="text-sm text-slate-600">Attach file (PDF, PNG, JPG, TXT, DOCX; max 5 MB)<input type="file" accept=".pdf,.png,.jpg,.jpeg,.txt,.docx" onChange={(event) => setAttachment(event.target.files?.[0] || null)} className="mt-2 block max-w-full text-sm" /></label><button disabled={!body.trim() && !attachment} className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white disabled:opacity-50" >Send reply</button></div>
          </form>
        </section>

        {canFeedback && <section className="mt-5 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-900">Rate your support experience</h2>
          {feedbackSent ? <p className="mt-3 text-green-700">Thank you. Your feedback was submitted.</p> : <form onSubmit={submitFeedback} className="mt-4 space-y-4">
            <label className="block text-sm font-medium">Rating<select value={rating} onChange={(event) => setRating(event.target.value)} className="mt-2 block rounded-lg border border-slate-300 px-3 py-2">{[5,4,3,2,1].map((value) => <option key={value} value={value}>{value} / 5</option>)}</select></label>
            <textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={3} className="w-full rounded-lg border border-slate-300 p-3" placeholder="Optional comments..." />
            <button className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white">Submit feedback</button>
          </form>}
        </section>}
      </div>
    </CustomerLayout>
  );
}

export default TicketDetail;
