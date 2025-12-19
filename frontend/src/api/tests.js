import apiClient from './client';

export const testsApi = {
  getAll: (params) =>
    apiClient.get('/tests/templates', { params }),
  
  getById: (id) =>
    apiClient.get(`/tests/templates/${id}`),
  
  startAttempt: (templateId) =>
    apiClient.post('/tests/attempts', { test_template_id: templateId }),
  
  getAttemptById: (attemptId) =>
    apiClient.get(`/tests/attempts/${attemptId}`),
  
  submitAttempt: (attemptId) =>
    apiClient.put(`/tests/attempts/${attemptId}/submit`),
  
  getMyAttempts: () =>
    apiClient.get('/tests/attempts/me'),
};
