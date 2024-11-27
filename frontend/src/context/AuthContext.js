import React, { createContext, useState, useEffect, useCallback } from 'react';
import { jwtDecode } from 'jwt-decode';
import api from '../api/api';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [authTokens, setAuthTokens] = useState(() => {
    const access = localStorage.getItem('access_token');
    const refresh = localStorage.getItem('refresh_token');
    return access && refresh ? { access, refresh } : null;
  });
  const [user, setUser] = useState(() => {
    if (authTokens) {
      try {
        return jwtDecode(authTokens.access);
      } catch (error) {
        console.error('Error al decodificar el token', error);
        return null;
      }
    }
    return null;
  });

  const [isAdmin, setIsAdmin] = useState(() => {
    if (authTokens) {
      try {
        const decoded = jwtDecode(authTokens.access);
        return decoded.is_staff || false;
      } catch (error) {
        console.error('Error al decodificar el token', error);
        return false;
      }
    }
    return false;
  });

  const loginUser = async (username, password) => {
    try {
      const response = await api.post('token/', {
        username,
        password,
      });
      setAuthTokens(response.data);
      const decodedUser = jwtDecode(response.data.access);
      setUser(decodedUser);
      setIsAdmin(decodedUser.is_staff || false);
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      enqueueSnackbar('Inicio de sesión exitoso', { variant: 'success' });
      navigate('/products');
    } catch (error) {
      console.error('Error al iniciar sesión', error);
      enqueueSnackbar('Credenciales inválidas', { variant: 'error' });
      throw error;
    }
  };

  const logoutUser = useCallback(() => {
    setAuthTokens(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    enqueueSnackbar('Sesión cerrada', { variant: 'info' });
    navigate('/login');
  }, [enqueueSnackbar, navigate]);

  const registerUser = async (userData) => {
    try {
      await api.post('users/register/', userData);
      enqueueSnackbar('Registro exitoso. Iniciando sesión...', { variant: 'success' });
      await loginUser(userData.username, userData.password);
    } catch (error) {
      console.error('Error al registrar usuario', error);
      const message =
        error.response && error.response.data
          ? Object.values(error.response.data).join(' ')
          : 'Error al registrar usuario';
      enqueueSnackbar(message, { variant: 'error' });
      throw error;
    }
  };

  const refreshToken = useCallback(async () => {
    const refresh = localStorage.getItem('refresh_token');
    if (refresh) {
      try {
        const response = await api.post('token/refresh/', { refresh });
        setAuthTokens((prev) => ({
          ...prev,
          access: response.data.access,
        }));
        const decodedUser = jwtDecode(response.data.access);
        setUser(decodedUser);
        setIsAdmin(decodedUser.is_staff || false);
        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers['Authorization'] = 'Bearer ' + response.data.access;
        enqueueSnackbar('Token renovado', { variant: 'info' });
      } catch (error) {
        console.error('Error al renovar el token', error);
        logoutUser();
      }
    } else {
      logoutUser();
    }
  }, [enqueueSnackbar, logoutUser]);;

  useEffect(() => {
    const interval = setInterval(() => {
      if (authTokens) {
        const decoded = jwtDecode(authTokens.access);
        const exp = decoded.exp * 1000;
        const now = Date.now();
        if (exp - now < 60000) {
          refreshToken();
        }
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [authTokens, refreshToken]);

  return (
    <AuthContext.Provider value={{ user, authTokens, isAdmin, loginUser, logoutUser, registerUser }}>
      {children}
    </AuthContext.Provider>
  );
};
