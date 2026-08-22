import { api } from '../../config/api';

export const publishTrip = async (tripId) => {
  const response = await api.post(`/api/trips/${tripId}/share`);
  return response.data;
};

export const unpublishTrip = async (tripId) => {
  const response = await api.delete(`/api/trips/${tripId}/share`);
  return response.data;
};

// This endpoint does not require authentication
export const getPublicItinerary = async (slug) => {
  const response = await api.get(`/api/public/itinerary/${slug}`);
  return response.data;
};

// This endpoint requires the user to be logged in so they can copy it to their account
export const copyTrip = async (slug, newName = null) => {
  const payload = newName ? { name: newName } : {};
  const response = await api.post(`/api/public/itinerary/${slug}/copy`, payload);
  return response.data;
};