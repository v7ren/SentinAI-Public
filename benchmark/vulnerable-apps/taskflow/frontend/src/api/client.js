import axios from 'axios';
import { getToken } from '../utils/authUtils';

const baseURL = 'http://localhost:3001';

const client = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (import.meta.env.DEV) console.log('API request', config.method, config.url, config.headers);
  return config;
});

client.interceptors.response.use(
  (res) => {
    if (import.meta.env.DEV) console.log('API response', res.config.url, res.status, res.data);
    return res;
  },
  (err) => {
    if (err.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default client;
