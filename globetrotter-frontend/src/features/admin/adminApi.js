import { api } from '../../config/api';

export const getStatsOverview = async () => {
  const response = await api.get('/api/admin/stats/overview');
  return response.data;
};

export const getTopCities = async (limit = 10) => {
  const response = await api.get(`/api/admin/stats/top-cities?limit=${limit}`);
  return response.data;
};

export const getTopActivities = async (limit = 10) => {
  const response = await api.get(`/api/admin/stats/top-activities?limit=${limit}`);
  return response.data;
};

export const getUsers = async (search = '', page = 1) => {
  const params = { page, page_size: 20 };
  if (search) params.search = search;
  const response = await api.get('/api/admin/users', { params });
  return response.data;
};