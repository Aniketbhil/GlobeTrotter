import { api } from '../../config/api';

export const getGroupedTrips = async () => {
  const response = await api.get('/api/trips', {
    params: { group_by: 'status' }
  });
  return response.data;
};