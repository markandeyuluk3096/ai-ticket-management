
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    phone_number: '',
    password: '',
    confirm_password: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    setLoading(true);

    try {
      const response = await api.post(
        'accounts/register/',
        formData
      );

      setSuccess(response.data.message);

      setTimeout(() => {
        navigate('/login');
      }, 1500);

    } catch (err) {
      const data = err.response?.data;

      if (data) {
        const messages = Object.entries(data)
          .map(([field, errors]) =>
            `${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`
          );

        setError(messages.join(' | '));
      } else {
        setError('Unable to connect to the server. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-lg p-8">

        <h1 className="text-3xl font-bold text-center text-blue-600">
          Create Account
        </h1>

        <p className="text-center text-gray-500 mt-2">
          Register for AI Ticket Management
        </p>

        {error && (
          <p className="bg-red-100 text-red-700 p-3 rounded-lg mt-5">
            {error}
          </p>
        )}

        {success && (
          <p className="bg-green-100 text-green-700 p-3 rounded-lg mt-5">
            {success}
          </p>
        )}

        <form onSubmit={handleSubmit} className="mt-8 space-y-4">

          <input name="first_name" value={formData.first_name} onChange={handleChange} required className="w-full border rounded-lg p-3" placeholder="First Name" />

          <input name="last_name" value={formData.last_name} onChange={handleChange} required className="w-full border rounded-lg p-3" placeholder="Last Name" />

          <input name="username" value={formData.username} onChange={handleChange} required className="w-full border rounded-lg p-3" placeholder="Username" />

          <input name="email" value={formData.email} onChange={handleChange} required type="email" className="w-full border rounded-lg p-3" placeholder="Email Address" />

          <input name="phone_number" value={formData.phone_number} onChange={handleChange} required type="tel" className="w-full border rounded-lg p-3" placeholder="Phone Number" />

          <input name="password" value={formData.password} onChange={handleChange} required type="password" className="w-full border rounded-lg p-3" placeholder="Password" />

          <input name="confirm_password" value={formData.confirm_password} onChange={handleChange} required type="password" className="w-full border rounded-lg p-3" placeholder="Confirm Password" />

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Registering...' : 'Create Account'}
          </button>

        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-blue-600 font-semibold">
            Login
          </Link>
        </p>

      </div>
    </div>
  );
}

export default Register;
