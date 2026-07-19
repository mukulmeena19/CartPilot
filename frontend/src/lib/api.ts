import axios from 'axios';

let rawUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
rawUrl = rawUrl.replace(/\/$/, ''); // Remove trailing slash if user added one
const API_URL = rawUrl.endsWith('/api/v1') ? rawUrl : `${rawUrl}/api/v1`;

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Crucial for sending HttpOnly cookies
});

// Request interceptor for adding the auth token
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling 401s and silent refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt silent refresh
        // Note: The refresh_token HttpOnly cookie is automatically sent because of withCredentials: true
        const { data } = await axios.post(`${API_URL}/auth/refresh`, {}, { withCredentials: true });
        
        // Save new access token
        if (typeof window !== 'undefined') {
          localStorage.setItem('token', data.access_token);
        }
        
        // Update header and retry original request
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed (token expired or revoked), logout user
        if (typeof window !== 'undefined') {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
