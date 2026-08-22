import { api } from '../../config/api';

export const getGroupedTrips = async () => {
  const response = await api.get('/api/trips', {
    params: { group_by: 'status' }
  });
  return response.data;
};

export const createTrip = async (tripData) => {
  const response = await api.post('/api/trips', tripData);
  return response.data;
};

export const deleteTrip = async (tripId) => {
  const response = await api.delete(`/api/trips/${tripId}`);
  return response.data;
};