import { useState, useCallback } from 'react';
import { apiClient } from '@/api/client';
import type { MesModel, SearchParams, ApiResponse } from '@/types/mes';

export function useSearch<T extends MesModel>(model: string) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const search = useCallback(
    async (params: SearchParams = {}) => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.search<T>(model, params);
        if (response.success && response.data) {
          setData(response.data);
          setTotal(response.total || 0);
        } else {
          setError(response.error || 'Search failed');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    },
    [model]
  );

  return { data, loading, error, total, search };
}

export function useCrud<T extends MesModel>(model: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const create = useCallback(
    async (values: Partial<T>): Promise<ApiResponse<T>> => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.create<T>(model, values);
        if (!response.success) {
          setError(response.error || 'Create failed');
        }
        return response;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMsg);
        return { success: false, error: errorMsg };
      } finally {
        setLoading(false);
      }
    },
    [model]
  );

  const update = useCallback(
    async (ids: number[], values: Partial<T>): Promise<ApiResponse<boolean>> => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.write<T>(model, ids, values);
        if (!response.success) {
          setError(response.error || 'Update failed');
        }
        return response;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMsg);
        return { success: false, error: errorMsg };
      } finally {
        setLoading(false);
      }
    },
    [model]
  );

  const remove = useCallback(
    async (ids: number[]): Promise<ApiResponse<boolean>> => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.unlink(model, ids);
        if (!response.success) {
          setError(response.error || 'Delete failed');
        }
        return response;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMsg);
        return { success: false, error: errorMsg };
      } finally {
        setLoading(false);
      }
    },
    [model]
  );

  return { create, update, remove, loading, error };
}

export function useModelAction<T = unknown>(model: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const callMethod = useCallback(
    async (
      method: string,
      args: unknown[] = [],
      kwargs: Record<string, unknown> = {}
    ): Promise<ApiResponse<T>> => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.callMethod<T>(model, method, args, kwargs);
        if (!response.success) {
          setError(response.error || 'Method call failed');
        }
        return response;
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
        setError(errorMsg);
        return { success: false, error: errorMsg };
      } finally {
        setLoading(false);
      }
    },
    [model]
  );

  return { callMethod, loading, error };
}
