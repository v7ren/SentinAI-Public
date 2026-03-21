import client from './client';

export const list = (params) => client.get('/api/v1/projects', { params });
export const getOne = (projectId) => client.get(`/api/v1/projects/${projectId}`);
export const create = (data) => client.post('/api/v1/projects', data);
export const update = (projectId, data) => client.put(`/api/v1/projects/${projectId}`, data);
export const remove = (projectId) => client.delete(`/api/v1/projects/${projectId}`);
