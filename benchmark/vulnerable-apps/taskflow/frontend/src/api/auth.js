import client from './client';

export const login = (email, password) =>
  client.post('/api/v1/auth/login', { email, password });

export const register = (email, password, fullName) =>
  client.post('/api/v1/auth/register', { email, password, fullName });

export const logout = () => client.post('/api/v1/auth/logout');
export const refreshToken = (refreshToken) =>
  client.post('/api/v1/auth/refresh', { refreshToken });
