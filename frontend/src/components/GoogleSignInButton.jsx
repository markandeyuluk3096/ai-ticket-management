import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

function GoogleSignInButton() {
  const buttonRef = useRef(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId || !buttonRef.current) return undefined;
    let cancelled = false;

    const initialize = () => {
      if (cancelled || !window.google?.accounts?.id || !buttonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async ({ credential }) => {
          setError('');
          try {
            const response = await api.post('accounts/google/', { credential });
            const { access, refresh } = response.data;
            const profile = await api.get('accounts/profile/', {
              headers: { Authorization: `Bearer ${access}` },
            });
            login(profile.data, access, refresh);
            navigate('/dashboard');
          } catch (err) {
            setError(err.response?.data?.detail || 'Google sign-in failed. Please try again.');
          }
        },
      });
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: 'outline',
        size: 'large',
        shape: 'rectangular',
        text: 'continue_with',
        width: 360,
      });
    };

    if (window.google?.accounts?.id) {
      initialize();
      return () => { cancelled = true; };
    }

    let script = document.querySelector('script[data-google-identity]');
    const onLoad = () => initialize();
    if (!script) {
      script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.dataset.googleIdentity = 'true';
      document.head.appendChild(script);
    }
    script.addEventListener('load', onLoad);
    return () => {
      cancelled = true;
      script?.removeEventListener('load', onLoad);
    };
  }, [clientId, login, navigate]);

  if (!clientId) {
    return <p className="mt-4 text-center text-xs text-slate-400">Google sign-in can be enabled by configuring VITE_GOOGLE_CLIENT_ID.</p>;
  }

  return <div className="mt-5">
    <div ref={buttonRef} className="flex justify-center" />
    {error && <p className="mt-3 text-sm text-red-600" role="alert">{error}</p>}
  </div>;
}

export default GoogleSignInButton;
