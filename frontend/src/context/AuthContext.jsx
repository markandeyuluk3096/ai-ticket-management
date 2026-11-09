
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [token, setToken] = useState(() => {
    return localStorage.getItem('access_token');
  });

  const login = (userData, accessToken) => {
    setUser(userData);
    setToken(accessToken);

    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('access_token', accessToken);
  };

  const logout = () => {
    setUser(null);
    setToken(null);

    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
