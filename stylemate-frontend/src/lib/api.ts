// src/lib/api.ts
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_BASE}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;

  // Create headers object (we'll conditionally add Content-Type)
  const headers = new Headers(options.headers || {});

  // Only set application/json if:
  // - body exists
  // - body is NOT FormData
  // - Content-Type is not already set by caller
  if (
    options.body &&
    !(options.body instanceof FormData) &&
    !headers.has('Content-Type')
  ) {
    headers.set('Content-Type', 'application/json');
  }

  // Optional: Add auth token if you have one stored
  // const token = localStorage.getItem('token');
  // if (token) {
  //   headers.set('Authorization', `Bearer ${token}`);
  // }

  const mergedOptions: RequestInit = {
    ...options,
    headers,
    // credentials: 'include', // uncomment if you use cookies/sessions
  };

  return fetch(url, mergedOptions);
}

// Convenience wrapper for JSON POST requests (keeps old behavior)
export async function postJson<T>(endpoint: string, body: any): Promise<T> {
  const res = await apiFetch(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || `Request failed: ${res.status}`);
  }

  return res.json();
}

// Optional: Add a typed wrapper specifically for file uploads if you want
// (not required — apiFetch already handles FormData correctly now)
export async function postFormData<T>(endpoint: string, formData: FormData): Promise<T> {
  const res = await apiFetch(endpoint, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || err.message || `Request failed: ${res.status}`);
  }

  return res.json();
}