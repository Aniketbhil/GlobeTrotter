import { api } from '../../config/api';

export const login = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await api.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const signup = async (userData) => {
  const response = await api.post('/api/auth/signup', userData);
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};