import { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for token on app load
    const token = localStorage.getItem('token');
    if (token) {
      setUser({ token }); 
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      // 1. Call Backend
      const { data } = await api.post('/auth/login', { email, password });
      
      // 2. Validate Response
      if (!data.access_token) {
        throw new Error("Login succeeded but no token returned!");
      }

      // 3. Store Token (CRITICAL STEP)
      console.log("Saving token:", data.access_token.substring(0, 10) + "...");
      localStorage.setItem('token', data.access_token);
      
      // 4. Update State
      setUser({ token: data.access_token });
      
      return true;
    } catch (err) {
      console.error("Login failed:", err);
      const msg = err.response?.data?.detail?.[0]?.msg || "Login failed";
      // toast.error(msg); // Optional: let the Login page handle the toast
      throw err;
    }
  };

  const logout = () => {
    console.log("Logging out...");
    localStorage.removeItem('token');
    setUser(null);
    window.location.href = '/login';
  };

  const register = async (email, password) => {
    await api.post('/auth/register', { email, password });
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);