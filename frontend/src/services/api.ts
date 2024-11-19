import axios, { AxiosResponse } from 'axios';

// APIクライアントの設定
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 100秒のタイムアウト
});

// レスポンス型の定義
export interface SearchResponse {
  answer: string;
  sources: Array<{
    content: string;
    metadata?: {
      source?: string;
    };
  }>;
}

export interface StatsResponse {
  total_documents: number;
  total_chunks: number;
  sources: Array<{
    url: string;
    title: string;
    chunk_count: number;
    added_at: string;
  }>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface AddDocumentResponse {
  status: string;
  message: string;
  url: string;
}

// リクエスト型の定義
export interface SearchRequest {
  query: string;
  model_type?: string;  // モデルタイプを追加ng;
}

export interface AddDocumentRequest {
  url: string;
  category: string;
  tags?: string[];
}

export const search = (request: SearchRequest): Promise<AxiosResponse<SearchResponse>> => {
  return apiClient.post<SearchResponse>('/search', request)
    .then(response => {
      // 余分なデータを除去して必要なデータのみを返す
      const { answer, sources } = response.data;
      return {
        ...response,
        data: { answer, sources }
      };
    });
};

// モデル切り替え用の新しい関数
export const switchModel = (model_type: string) => 
  apiClient.post('/model/switch', { model_type });

export const addDocument = (request: AddDocumentRequest): Promise<AxiosResponse<AddDocumentResponse>> => 
  apiClient.post<AddDocumentResponse>('/documents/add', request);

export const getStats = (): Promise<AxiosResponse<StatsResponse>> => 
  apiClient.get<StatsResponse>('/stats');

export const getHealth = (): Promise<AxiosResponse<HealthResponse>> => 
  apiClient.get<HealthResponse>('/health');

// エラー型の定義
export interface ApiError {
  detail: string;
  status_code?: number;
}

// エラーハンドリング用のインターセプター
apiClient.interceptors.response.use(
  (response) => {
    // 成功レスポンスの処理
    return response;
  },
  (error) => {
    // エラーレスポンスの処理
    if (error.response) {
      // サーバーからのエラーレスポンス
      console.error('API Error:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
      });
      
      const errorMessage = error.response.data.detail || 'An unexpected error occurred';
      throw new Error(errorMessage);
    } else if (error.request) {
      // リクエストは送信されたがレスポンスがない
      console.error('Network Error:', error.request);
      throw new Error('Network error - no response received');
    } else {
      // リクエストの設定時にエラーが発生
      console.error('Request Error:', error.message);
      throw new Error('Request configuration error');
    }
  }
);

// APIクライアントのデフォルトヘッダーを設定する関数
export const setAuthToken = (token: string): void => {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
};

// APIクライアントのデフォルトヘッダーをクリアする関数
export const clearAuthToken = (): void => {
  delete apiClient.defaults.headers.common['Authorization'];
};

// レスポンスの型ガード
export const isSearchResponse = (data: any): data is SearchResponse => {
  return 'answer' in data && 'sources' in data;
};

export const isStatsResponse = (data: any): data is StatsResponse => {
  return 'total_documents' in data && 'total_chunks' in data && 'sources' in data;
};

export const isHealthResponse = (data: any): data is HealthResponse => {
  return 'status' in data && 'timestamp' in data;
};

// エクスポートするデフォルトコンフィグ
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000/api',
  TIMEOUT: 100000,
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
  },
};

export default apiClient;