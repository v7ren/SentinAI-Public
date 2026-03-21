import client from './client';

export const list = (params) => client.get('/api/v1/tasks', { params });
export const getOne = (taskId) => client.get(`/api/v1/tasks/${taskId}`);
export const create = (data) => client.post('/api/v1/tasks', data);
export const update = (taskId, data) => client.put(`/api/v1/tasks/${taskId}`, data);
export const remove = (taskId) => client.delete(`/api/v1/tasks/${taskId}`);
