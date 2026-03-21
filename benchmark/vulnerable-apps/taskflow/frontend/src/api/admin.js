import client from './client';

export const getAllUsers = () => client.get('/api/v1/admin/users');
export const deleteUser = (id) => client.delete(`/api/v1/admin/users/${id}`);
export const getBillingOverview = () => client.get('/api/v1/admin/billing');
