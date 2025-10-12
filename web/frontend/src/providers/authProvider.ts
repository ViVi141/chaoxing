import { AuthBindings } from '@refinedev/core';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理401
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authProvider: AuthBindings = {
  login: async ({ username, password }) => {
    try {
      // 清除旧token
      localStorage.removeItem('token');
      
      const response = await axios.post(`${API_URL}/auth/login`, 
        new URLSearchParams({
          username,
          password,
        }), 
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        return {
          success: true,
          redirectTo: '/',
        };
      }

      return {
        success: false,
        error: {
          message: '登录失败',
          name: 'Login Error',
        },
      };
    } catch (error: any) {
      return {
        success: false,
        error: {
          message: error.response?.data?.detail || '登录失败',
          name: 'Login Error',
        },
      };
    }
  },

  logout: async () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return {
      success: true,
      redirectTo: '/login',
    };
  },

  check: async () => {
    const token = localStorage.getItem('token');
    if (token) {
      return {
        authenticated: true,
      };
    }

    return {
      authenticated: false,
      redirectTo: '/login',
      logout: true,
    };
  },

  getPermissions: async () => {
    const user = localStorage.getItem('user');
    if (user) {
      const userData = JSON.parse(user);
      return userData.role || 'user';
    }
    return null;
  },

  getIdentity: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      return null;
    }

    try {
      const response = await axiosInstance.get('/auth/me');
      return response.data;
    } catch {
      return null;
    }
  },

  onError: async (error) => {
    if (error.response?.status === 401) {
      return {
        logout: true,
        redirectTo: '/login',
        error,
      };
    }

    return { error };
  },
};

export { axiosInstance };

