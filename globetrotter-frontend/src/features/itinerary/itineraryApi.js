import { api } from '../../config/api';

export const getItinerary = async (tripId) => {
  const response = await api.get(`/api/trips/${tripId}/itinerary`);
  return response.data;
};

export const addStop = async (tripId, stopData) => {
  const response = await api.post(`/api/trips/${tripId}/stops`, stopData);
  return response.data;
};

export const getCities = async () => {
  const response = await api.get('/api/cities?page_size=100');
  return response.data;
};

// NEW: Fetch activities based on city and optional search/type filters
export const getActivities = async (cityId, search = '') => {
  const params = { city_id: cityId, page_size: 50 };
  if (search) params.search = search;
  
  const response = await api.get('/api/activities', { params });
  return response.data;
};

// NEW: Add an activity to a specific stop on a specific date
export const addTripActivity = async (tripId, stopId, activityData) => {
  const response = await api.post(`/api/trips/${tripId}/stops/${stopId}/activities`, activityData);
  return response.data;
};

export const deleteStop = async (tripId, stopId) => {
  const response = await api.delete(`/api/trips/${tripId}/stops/${stopId}`);
  return response.data;
};

export const deleteTripActivity = async (tripId, stopId, activityId) => {
  const response = await api.delete(`/api/trips/${tripId}/stops/${stopId}/activities/${activityId}`);
  return response.data;
};