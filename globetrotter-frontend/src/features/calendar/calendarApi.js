import { api } from '../../config/api';

export const getMonthCalendar = async (year, month) => {
  const params = {};
  if (year) params.year = year;
  if (month) params.month = month;
  
  const response = await api.get('/api/trips/calendar', { params });
  return response.data;
};