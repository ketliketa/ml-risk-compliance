import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for friendly error messages
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      error.message = 'Cannot connect to server. Please ensure the backend is running on http://127.0.0.1:8000';
    } else if (error.response) {
      // Server responded with error status
      error.message = error.response.data?.detail || error.response.data?.message || `Server error: ${error.response.status}`;
    } else if (error.request) {
      error.message = 'No response from server. Please check your connection.';
    }
    return Promise.reject(error);
  }
);

export default api;
