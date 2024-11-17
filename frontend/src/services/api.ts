import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const addDocument = (document: object) => apiClient.post('/documents/add', document);
export const search = (query: object) => apiClient.post('/search', query);
export const getStats = () => apiClient.get('/stats');
export const getHealth = () => apiClient.get('/health');
