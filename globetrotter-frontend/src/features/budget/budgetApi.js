import { api } from '../../config/api';

export const getTripBudget = async (tripId, threshold = null) => {
  const params = threshold ? { daily_budget_threshold: threshold } : {};
  const response = await api.get(`/api/trips/${tripId}/budget`, { params });
  return response.data;
};

export const updateStopBudgetOverride = async (tripId, stopId, data) => {
  const response = await api.put(`/api/trips/${tripId}/stops/${stopId}/budget-override`, data);
  return response.data;
};