import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

let refreshPromise = null;

const clearStoredSession = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

api.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem('access_token');

  if (accessToken && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const requestUrl = originalRequest?.url || '';
    const isAuthenticationRequest =
      requestUrl.includes('accounts/login/') ||
      requestUrl.includes('accounts/register/') ||
      requestUrl.includes('accounts/logout/') ||
      requestUrl.includes('token/refresh/');

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      isAuthenticationRequest
    ) {
      return Promise.reject(error);
    }

    const refreshToken = localStorage.getItem('refresh_token');

    if (!refreshToken) {
      clearStoredSession();
      if (window.location.pathname !== '/login') {
        window.location.assign('/login');
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      if (!refreshPromise) {
        refreshPromise = axios
          .post(`${baseURL}token/refresh/`, { refresh: refreshToken })
          .then(({ data }) => {
            localStorage.setItem('access_token', data.access);
            if (data.refresh) {
              localStorage.setItem('refresh_token', data.refresh);
            }
            return data.access;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const newAccessToken = await refreshPromise;
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      const refreshStatus = refreshError.response?.status;

      if (refreshStatus === 400 || refreshStatus === 401) {
        clearStoredSession();
        if (window.location.pathname !== '/login') {
          window.location.assign('/login');
        }
      }

      return Promise.reject(refreshError);
    }
  }
);

export default api;
