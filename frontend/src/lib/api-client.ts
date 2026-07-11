export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export interface ApiErrorPayload {
  detail: string;
  trace_id?: string;
  [key: string]: unknown;
}

export class ApiError extends Error {
  public status: number;
  public payload: ApiErrorPayload;

  constructor(status: number, payload: ApiErrorPayload) {
    super(payload.detail || `API error ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.payload = payload;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ApiErrorPayload = { detail: "Unknown error" };
    try {
      payload = await response.json();
    } catch {
      const text = await response.text();
      payload = { detail: text };
    }
    
    if (response.status === 401 || response.status === 403) {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
    }
    
    throw new ApiError(response.status, payload);
  }
  return response.json() as Promise<T>;
}

function getHeaders(customHeaders?: HeadersInit): Headers {
  const headers = new Headers(customHeaders);
  headers.set('content-type', 'application/json');
  
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    headers.set('X-Trace-ID', crypto.randomUUID());
  } else {
    // fallback for environments without crypto.randomUUID (e.g. some older test environments)
    headers.set('X-Trace-ID', `trace-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`);
  }
  
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }
  return headers;
}

export async function apiGet<T>(path: string, headers?: HeadersInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: getHeaders(headers),
  });
  return handleResponse<T>(response);
}

export async function apiPost<T>(path: string, body: unknown, headers?: HeadersInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: getHeaders(headers),
    body: JSON.stringify(body),
  });
  return handleResponse<T>(response);
}

export async function apiPut<T>(path: string, body: unknown, headers?: HeadersInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "PUT",
    headers: getHeaders(headers),
    body: JSON.stringify(body),
  });
  return handleResponse<T>(response);
}

export async function apiDelete<T>(path: string, headers?: HeadersInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "DELETE",
    headers: getHeaders(headers),
  });
  return handleResponse<T>(response);
}
