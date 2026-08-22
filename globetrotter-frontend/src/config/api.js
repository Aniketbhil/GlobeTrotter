import axios from 'axios';

// Connects to your FastAPI backend running locally
export const api = axios.create({
  baseURL: 'http://localhost:8000', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach the JWT token if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('globeTrotter_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});