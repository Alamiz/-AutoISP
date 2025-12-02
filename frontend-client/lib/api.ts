const LOCAL_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
const MASTER_API_URL = process.env.NEXT_PUBLIC_MASTER_API_URL || "http://localhost:8000";

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

type ApiType = "local" | "master";

interface ApiConfig {
  baseUrl: string;
  headers: HeadersInit;
}

function getApiConfig(apiType: ApiType): ApiConfig {
  const baseUrl = apiType === "master" ? MASTER_API_URL : LOCAL_API_URL;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (apiType === "master") {
    const tokensStr = typeof window !== 'undefined' ? localStorage.getItem("auth_tokens") : null;
    if (tokensStr) {
      try {
        const tokens = JSON.parse(tokensStr);
        if (tokens.access) {
          headers["Authorization"] = `Bearer ${tokens.access}`;
        }
      } catch (e) {
        // Silent fail
      }
    }
  }

  return { baseUrl, headers };
}

export async function apiGet<T>(endpoint: string, apiType: ApiType = "master"): Promise<T> {
  const { baseUrl, headers } = getApiConfig(apiType);

  // GET requests usually don't have Content-Type, but it doesn't hurt. 
  // However, we should remove it if it causes issues with some servers.
  // For now, keeping it as getApiConfig adds it.

  const res = await fetch(`${baseUrl}${endpoint}`, { headers });
  if (!res.ok) throw new Error(`Failed to fetch ${endpoint}: ${res.status}`);
  return res.json();
}

export async function apiPost<T, B>(
  endpoint: string,
  body: B,
  apiType: ApiType = "master"
): Promise<T> {
  const { baseUrl, headers } = getApiConfig(apiType);

  const res = await fetch(`${baseUrl}${endpoint}`, {
    method: "POST",
    headers,
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

export async function apiPut<T, B>(
  endpoint: string,
  body: B,
  apiType: ApiType = "master"
): Promise<T> {
  const { baseUrl, headers } = getApiConfig(apiType);

  const res = await fetch(`${baseUrl}${endpoint}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`Failed to put to ${endpoint}: ${res.status}`);
  return res.json();
}

export async function apiPatch<T, B>(
  endpoint: string,
  body: B,
  apiType: ApiType = "master"
): Promise<T> {
  const { baseUrl, headers } = getApiConfig(apiType);

  const res = await fetch(`${baseUrl}${endpoint}`, {
    method: "PATCH",
    headers,
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
      `Failed to patch to ${endpoint}: ${res.status}`;
    throw new ApiError(message, res.status, data as ApiErrorDetails);
  }

  return data as T;
}

export async function apiDelete<T, B>(
  endpoint: string,
  body?: B,
  apiType: ApiType = "master"
): Promise<T> {
  const { baseUrl, headers } = getApiConfig(apiType);

  const res = await fetch(`${baseUrl}${endpoint}`, {
    method: "DELETE",
    headers,
    ...(body && { body: JSON.stringify(body) })
  });

  // Throw error if not ok
  if (!res.ok) throw new Error(`Failed to delete ${endpoint}: ${res.status}`);

  // Return null if no content
  if (res.status === 204) return null as any;

  return res.json();
}