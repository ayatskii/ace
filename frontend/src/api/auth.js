import apiClient from './client';

export const authApi = {
  login: (email, password) =>
    apiClient.post('/auth/login', { email, password }),
  
  register: (data) =>
    apiClient.post('/auth/register', data),
  
  refreshToken: () =>
    apiClient.post('/auth/refresh'),
  
  getCurrentUser: () =>
    apiClient.get('/users/me'),
};
