import { api } from '../../config/api';

export const searchCities = async (searchQuery = '') => {
  const params = { page_size: 50 };
  if (searchQuery) params.search = searchQuery;
  
  const response = await api.get('/api/cities', { params });
  return response.data;
};

export const searchActivities = async (searchQuery = '') => {
  const params = { page_size: 50 };
  if (searchQuery) params.search = searchQuery;
  
  const response = await api.get('/api/activities', { params });
  return response.data;
};