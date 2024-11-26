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

  const loginUser = async (username, password) => {
    try {
      const response = await api.post('token/', {
        username,
        password,
      });
      setAuthTokens(response.data);
      setUser(jwtDecode(response.data.access));
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
      const response = await api.post('users/register/', userData);
      enqueueSnackbar('Registro exitoso. Iniciando sesión...', { variant: 'success' });
      // Iniciar sesión automáticamente después del registro
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
        setUser(jwtDecode(response.data.access));
        localStorage.setItem('access_token', response.data.access);
        enqueueSnackbar('Token renovado', { variant: 'info' });
      } catch (error) {
        console.error('Error al renovar el token', error);
        logoutUser();
      }
    } else {
      logoutUser();
    }
  }, [enqueueSnackbar, logoutUser]);

  useEffect(() => {
    const checkTokenExpiration = () => {
      if (authTokens) {
        try {
          const decoded = jwtDecode(authTokens.access);
          const exp = decoded.exp * 1000; // Convertir a milisegundos
          const now = Date.now();
          if (exp - now < 60000) { // Si expira en menos de 1 minuto
            refreshToken();
          }
        } catch (error) {
          console.error('Error al verificar la expiración del token', error);
          logoutUser();
        }
      }
    };

    const interval = setInterval(checkTokenExpiration, 30000); // Verificar cada 30 segundos

    return () => clearInterval(interval);
  }, [authTokens, refreshToken, logoutUser]);

  return (
    <AuthContext.Provider value={{ user, authTokens, loginUser, logoutUser, registerUser }}>
      {children}
    </AuthContext.Provider>
  );
};
