import axios from 'axios';
import useSWR from 'swr';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_URL}/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// SWR fetcher
const fetcher = (url: string) => api.get(url).then((res) => res.data);

// Custom hooks for API calls
export function useProjects() {
  const { data, error, mutate } = useSWR('/projects', fetcher);
  
  return {
    projects: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useProject(projectId: string) {
  const { data, error, mutate } = useSWR(
    projectId ? `/projects/${projectId}` : null,
    fetcher
  );
  
  return {
    project: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useBlueprint(projectId: string) {
  const { data, error, mutate } = useSWR(
    projectId ? `/blueprints/${projectId}` : null,
    fetcher
  );
  
  return {
    blueprint: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useReadiness(projectId: string) {
  const { data, error, mutate } = useSWR(
    projectId ? `/runs/readiness/${projectId}` : null,
    fetcher
  );
  
  return {
    readiness: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useDashboard(projectId: string) {
  const { data, error, mutate } = useSWR(
    projectId ? `/dashboards/${projectId}` : null,
    fetcher
  );
  
  return {
    dashboard: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}

export function useReadiness(projectId: string) {
  const { data, error, mutate } = useSWR(
    projectId ? `/runs/readiness/${projectId}` : null,
    fetcher
  );
  
  return {
    readiness: data,
    isLoading: !error && !data,
    isError: error,
    mutate,
  };
}
