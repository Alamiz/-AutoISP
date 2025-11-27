const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiErrorDetails {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

export class ApiError extends Error {
  status: number;
  data?: ApiErrorDetails;

  constructor(message: string, status: number, data?: ApiErrorDetails) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`);
  if (!res.ok) throw new Error(`Failed to fetch ${endpoint}: ${res.status}`);
  return res.json();
}

export async function apiPost<T, B>(
  endpoint: string,
  body: B
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  let data: ApiErrorDetails | T | null = null;
  try {
    data = (await res.json()) as T;
  } catch {
    data = null;
  }

  if (!res.ok) {
    const message =
      (data as ApiErrorDetails)?.detail ||
      (data as ApiErrorDetails)?.message ||
      `Failed to post to ${endpoint}: ${res.status}`;
    throw new ApiError(message, res.status, data as ApiErrorDetails);
  }

  return data as T;
}

export async function apiPut<T, B>(endpoint: string, body: B): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Failed to put to ${endpoint}: ${res.status}`);
  return res.json();
}

export async function apiDelete<T, B>(endpoint: string, body?: B): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    ...(body && { body: JSON.stringify(body) })
  });
  if (!res.ok) throw new Error(`Failed to delete ${endpoint}: ${res.status}`);
  return res.json();
}