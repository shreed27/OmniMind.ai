import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { apiGet, apiPost, ApiError } from '../src/lib/api-client';

describe('api-client', () => {
  const mockFetch = vi.fn();
  
  beforeEach(() => {
    global.fetch = mockFetch;
    localStorage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('adds trace ID and authorization headers', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    });
    localStorage.setItem('auth_token', 'test_token');
    
    await apiGet('/test');
    
    expect(mockFetch).toHaveBeenCalledTimes(1);
    const [, options] = mockFetch.mock.calls[0];
    const headers = options.headers as Headers;
    
    expect(headers.get('Authorization')).toBe('Bearer test_token');
    expect(headers.has('X-Trace-ID')).toBe(true);
  });

  it('throws ApiError on failed request', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Bad request', trace_id: '123' })
    });

    await expect(apiGet('/test')).rejects.toThrowError(ApiError);
    
    try {
      await apiGet('/test');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      if (e instanceof ApiError) {
        expect(e.status).toBe(400);
        expect(e.payload.detail).toBe('Bad request');
      }
    }
  });

  it('dispatches auth:unauthorized on 401', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' })
    });

    const dispatchEventSpy = vi.spyOn(window, 'dispatchEvent');

    await expect(apiGet('/test')).rejects.toThrowError(ApiError);
    
    expect(dispatchEventSpy).toHaveBeenCalledTimes(1);
    const event = dispatchEventSpy.mock.calls[0][0] as CustomEvent;
    expect(event.type).toBe('auth:unauthorized');
    
    dispatchEventSpy.mockRestore();
  });
});
