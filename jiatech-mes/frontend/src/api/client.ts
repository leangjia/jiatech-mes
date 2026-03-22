import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiResponse, PaginatedResponse, SearchParams, MesModel } from '@/types/mes';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class MesApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.message);
        return Promise.reject(error);
      }
    );
  }

  async healthCheck(): Promise<ApiResponse> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async getModels(): Promise<ApiResponse<string[]>> {
    const response = await this.client.get('/models');
    return response.data;
  }

  async search<T extends MesModel>(
    model: string,
    params: SearchParams = {}
  ): Promise<PaginatedResponse<T>> {
    const response = await this.client.post(`/model/${model}/search`, params);
    return response.data;
  }

  async read<T extends MesModel>(
    model: string,
    ids: number[],
    fields?: string[]
  ): Promise<ApiResponse<T[]>> {
    const response = await this.client.post(`/model/${model}/read`, {
      ids,
      fields,
    });
    return response.data;
  }

  async create<T extends MesModel>(
    model: string,
    values: Partial<T>
  ): Promise<ApiResponse<T>> {
    const response = await this.client.post(`/model/${model}/create`, values);
    return response.data;
  }

  async write<T extends MesModel>(
    model: string,
    ids: number[],
    values: Partial<T>
  ): Promise<ApiResponse<boolean>> {
    const response = await this.client.post(`/model/${model}/write`, {
      ids,
      values,
    });
    return response.data;
  }

  async unlink(
    model: string,
    ids: number[]
  ): Promise<ApiResponse<boolean>> {
    const response = await this.client.post(`/model/${model}/unlink`, {
      ids,
    });
    return response.data;
  }

  async callMethod<T = unknown>(
    model: string,
    method: string,
    args: unknown[] = [],
    kwargs: Record<string, unknown> = {}
  ): Promise<ApiResponse<T>> {
    const response = await this.client.post(`/model/${model}/call`, {
      method,
      args,
      kwargs,
    });
    return response.data;
  }
}

export const apiClient = new MesApiClient();
export default apiClient;
