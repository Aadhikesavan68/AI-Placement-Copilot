import axios from 'axios';

const configuredApiHost = import.meta.env.VITE_API_URL || `${window.location.protocol}//127.0.0.1:8000`;
const apiHost = configuredApiHost.replace('://localhost', '://127.0.0.1').replace(/\/$/, '');

const api = axios.create({
  baseURL: `${apiHost}/api/v1`,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
