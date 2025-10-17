// API Service Layer for Academic Integrity Platform
// frontend/src/services/api.ts

import axios, { AxiosInstance, AxiosError } from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============= TYPE DEFINITIONS =============

export interface Paper {
  paper_id: string;
  title: string;
  authors: string[];
  abstract?: string;
  publication_date?: string;
  journal?: string;
  risk_score: number;
  status: 'queued' | 'processing' | 'completed' | 'failed';
}

export interface UploadResponse {
  paper_id: string;
  job_id: string;
  status: string;
  message: string;
}

export interface AnalysisResult {
  paper_id: string;
  overall_risk_score: number;
  similarity_findings: SimilarityFinding[];
  anomaly_findings: AnomalyFinding[];
  recommendations: string[];
  detailed_report_url: string;
}

export interface SimilarityFinding {
  paper_id: string;
  title: string;
  authors: string[];
  text_similarity: number;
  semantic_similarity: number;
  overall_similarity: number;
  publication_date?: string;
}

export interface AnomalyFinding {
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  confidence: number;
}

export interface JobStatus {
  job_id: string;
  status: string;
  progress: number;
  message?: string;
  result?: any;
}

export interface Statistics {
  total_papers: number;
  processed_papers: number;
  processing_rate: number;
  total_anomalies_detected: number;
  high_risk_papers: number;
  average_processing_time: string;
  last_updated: string;
}

export interface SearchParams {
  query?: string;
  author?: string;
  journal?: string;
  start_date?: string;
  end_date?: string;
  min_risk_score?: number;
  limit?: number;
  offset?: number;
}

export interface SearchResults {
  total: number;
  offset: number;
  limit: number;
  results: Paper[];
}

// ============= API METHODS =============

export const api = {
  // Health Check
  async healthCheck() {
    const response = await apiClient.get('/');
    return response.data;
  },

  // Papers API
  papers: {
    async upload(file: File, metadata?: any): Promise<UploadResponse> {
      const formData = new FormData();
      formData.append('file', file);
      if (metadata) {
        formData.append('metadata', JSON.stringify(metadata));
      }

      const response = await apiClient.post('/api/papers/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },

    async analyze(paperId: string): Promise<AnalysisResult> {
      const response = await apiClient.get(`/api/papers/${paperId}/analyze`);
      return response.data;
    },

    async checkSimilarity(
      paperId: string,
      options?: {
        check_types?: string[];
        threshold?: number;
        limit?: number;
      }
    ): Promise<SimilarityFinding[]> {
      const response = await apiClient.post(`/api/papers/${paperId}/similarity`, {
        paper_id: paperId,
        check_types: options?.check_types || ['text', 'semantic', 'image', 'data'],
        threshold: options?.threshold || 0.3,
        limit: options?.limit || 100,
      });
      return response.data;
    },

    async search(params: SearchParams): Promise<SearchResults> {
      const response = await apiClient.get('/api/papers/search', { params });
      return response.data;
    },

    async get(paperId: string): Promise<Paper> {
      const response = await apiClient.get(`/api/papers/${paperId}`);
      return response.data;
    },

    async delete(paperId: string): Promise<void> {
      await apiClient.delete(`/api/papers/${paperId}`);
    },
  },

  // Jobs API
  jobs: {
    async getStatus(jobId: string): Promise<JobStatus> {
      const response = await apiClient.get(`/api/jobs/${jobId}/status`);
      return response.data;
    },

    async pollStatus(
      jobId: string,
      onUpdate: (status: JobStatus) => void,
      interval: number = 2000
    ): Promise<JobStatus> {
      return new Promise((resolve, reject) => {
        const poll = setInterval(async () => {
          try {
            const status = await this.getStatus(jobId);
            onUpdate(status);

            if (status.status === 'completed' || status.status === 'failed') {
              clearInterval(poll);
              resolve(status);
            }
          } catch (error) {
            clearInterval(poll);
            reject(error);
          }
        }, interval);
      });
    },
  },

  // Statistics API
  statistics: {
    async getOverview(): Promise<Statistics> {
      const response = await apiClient.get('/api/statistics/overview');
      return response.data;
    },
  },

  // Batch Processing API
  batch: {
    async createJob(paperIds: string[], options?: any): Promise<{ job_id: string }> {
      const response = await apiClient.post('/api/batch/jobs', {
        paper_ids: paperIds,
        ...options,
      });
      return response.data;
    },

    async listJobs(): Promise<any[]> {
      const response = await apiClient.get('/api/batch/jobs');
      return response.data;
    },

    async getJobDetails(jobId: string): Promise<any> {
      const response = await apiClient.get(`/api/batch/jobs/${jobId}`);
      return response.data;
    },

    async cancelJob(jobId: string): Promise<void> {
      await apiClient.delete(`/api/batch/jobs/${jobId}`);
    },
  },

  // Image Forensics API
  images: {
    async analyzeImage(paperId: string, imageId: string): Promise<any> {
      const response = await apiClient.post(`/api/papers/${paperId}/images/${imageId}/analyze`);
      return response.data;
    },

    async detectManipulation(paperId: string): Promise<any> {
      const response = await apiClient.get(`/api/papers/${paperId}/images/manipulation`);
      return response.data;
    },
  },

  // Statistical Tests API
  statistical: {
    async runGRIM(paperId: string): Promise<any> {
      const response = await apiClient.post(`/api/papers/${paperId}/statistical/grim`);
      return response.data;
    },

    async runBenfordsLaw(paperId: string): Promise<any> {
      const response = await apiClient.post(`/api/papers/${paperId}/statistical/benfords`);
      return response.data;
    },

    async checkPHacking(paperId: string): Promise<any> {
      const response = await apiClient.post(`/api/papers/${paperId}/statistical/p-hacking`);
      return response.data;
    },
  },

  // Citation Network API
  citations: {
    async getNetwork(paperId: string): Promise<any> {
      const response = await apiClient.get(`/api/papers/${paperId}/citations/network`);
      return response.data;
    },

    async analyzeSelfCitations(paperId: string): Promise<any> {
      const response = await apiClient.get(`/api/papers/${paperId}/citations/self-citations`);
      return response.data;
    },
  },

  // AI Explainability API
  explainability: {
    async getLIME(paperId: string): Promise<any> {
      const response = await apiClient.get(`/api/papers/${paperId}/explainability/lime`);
      return response.data;
    },

    async getSHAP(paperId: string): Promise<any> {
      const response = await apiClient.get(`/api/papers/${paperId}/explainability/shap`);
      return response.data;
    },

    async getFeatureImportance(paperId: string): Promise<any> {
      const response = await apiClient.get(`/api/papers/${paperId}/explainability/features`);
      return response.data;
    },
  },

  // Collaboration API
  collaboration: {
    async getReviews(paperId: string): Promise<any[]> {
      const response = await apiClient.get(`/api/papers/${paperId}/reviews`);
      return response.data;
    },

    async addReview(paperId: string, review: any): Promise<any> {
      const response = await apiClient.post(`/api/papers/${paperId}/reviews`, review);
      return response.data;
    },

    async addComment(paperId: string, comment: string): Promise<any> {
      const response = await apiClient.post(`/api/papers/${paperId}/comments`, { text: comment });
      return response.data;
    },

    async getComments(paperId: string): Promise<any[]> {
      const response = await apiClient.get(`/api/papers/${paperId}/comments`);
      return response.data;
    },
  },
};

// Error handler utility
export const handleApiError = (error: any): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      return error.response.data?.detail || error.response.data?.message || 'An error occurred';
    } else if (error.request) {
      return 'No response from server. Please check your connection.';
    }
  }
  return 'An unexpected error occurred';
};

export default api;
