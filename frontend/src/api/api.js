import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/', // Cambia la URL si es necesario
});

// Interceptor para incluir el token en cada solicitud
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar la renovación de tokens
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');

      if (refreshToken) {
        try {
          const response = await axios.post('http://localhost:8000/api/v1/token/refresh/', {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access);
          api.defaults.headers['Authorization'] = 'Bearer ' + response.data.access;
          originalRequest.headers['Authorization'] = 'Bearer ' + response.data.access;
          return api(originalRequest);
        } catch (err) {
          console.error('No se pudo refrescar el token', err);
          // Redirigir al login si no se puede refrescar el token
          window.location.href = '/login';
          return Promise.reject(err);
        }
      } else {
        // Si no hay refresh token, redirigir al login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
