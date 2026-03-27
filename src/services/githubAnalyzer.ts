import type { SystemData } from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() || 'http://localhost:8000';

interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as ApiErrorPayload;
    if (payload?.error?.message) {
      return payload.error.message;
    }
  } catch {
    // Ignore parse errors and fallback to status text.
  }

  if (response.status === 404) {
    return 'Repository not found. Check owner/repo format.';
  }
  if (response.status === 422) {
    return 'Invalid request payload. Please check input fields.';
  }
  if (response.status >= 500) {
    return 'Backend error while analyzing repository.';
  }
  return `Request failed (${response.status})`;
}

export async function analyzeRepository(repoPath: string): Promise<SystemData> {
  const repo = repoPath
    .replace(/https?:\/\/github\.com\//i, '')
    .replace(/\.git$/i, '')
    .replace(/^\/|\/$/g, '');

  if (!repo || !repo.includes('/')) {
    throw new Error('Please enter a valid repository in owner/repo format.');
  }

  const response = await fetch(`${API_BASE_URL}/api/repository/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ repo }),
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return (await response.json()) as SystemData;
}

export async function getSystemData(): Promise<SystemData> {
  const response = await fetch(`${API_BASE_URL}/api/system-data`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return (await response.json()) as SystemData;
}
