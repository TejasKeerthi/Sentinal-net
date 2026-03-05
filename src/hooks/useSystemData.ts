import { useState, useCallback, useRef } from 'react';
import type { SystemData } from '../types';
import { mockSystemData } from '../data/mockData';

const API_BASE_URL = 'http://localhost:8000';

export const useSystemData = () => {
  const [data, setData] = useState<SystemData>(mockSystemData);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRepo, setCurrentRepo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const lastAnalyzedRepo = useRef<string | null>(null);

  /**
   * Load data from the backend API.
   * If repoUrl is given, calls /api/analyze-github which fetches real GitHub data.
   * Otherwise falls back to /api/system-data (mock from backend).
   * If the backend is unreachable, gracefully falls back to client-side mock data.
   */
  const loadData = useCallback(async (repoUrl?: string): Promise<boolean> => {
    try {
      const url = repoUrl
        ? `${API_BASE_URL}/api/analyze-github?repo=${encodeURIComponent(repoUrl)}`
        : `${API_BASE_URL}/api/system-data`;

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);

      const response = await fetch(url, { signal: controller.signal });
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const newData = await response.json();

      // Check for error response from GitHub analyzer
      if (newData.error) {
        setError(newData.message || newData.error);
        return false;
      }

      // Ensure failureRiskScore is always a clean integer 0-100
      if (newData.metrics && typeof newData.metrics.failureRiskScore === 'number') {
        newData.metrics.failureRiskScore = Math.round(
          Math.max(0, Math.min(100, newData.metrics.failureRiskScore))
        );
      }

      setData(newData);
      setError(null);
      if (repoUrl) {
        setCurrentRepo(repoUrl);
        lastAnalyzedRepo.current = repoUrl;
      }
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch data';

      // Don't show network errors as scary — just note the backend isn't running
      if (errorMessage.includes('fetch') || errorMessage.includes('network') || errorMessage.includes('abort') || errorMessage.includes('Failed')) {
        setError('Backend not running. Showing placeholder data. Start the backend with: cd backend && python main.py');
      } else {
        setError(errorMessage);
      }
      return false;
    }
  }, []);

  /**
   * Manual refresh. Re-analyzes the current repo if one was set,
   * otherwise fetches generic system data.
   */
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      if (currentRepo) {
        await loadData(currentRepo);
      } else {
        await loadData();
      }
    } finally {
      setIsLoading(false);
    }
  }, [currentRepo, loadData]);

  /**
   * Analyze a specific GitHub repository.
   * This is the primary action — fetches real data from GitHub via the backend.
   */
  const analyzeGitHubRepo = useCallback(async (repoUrl: string) => {
    if (!repoUrl.trim()) {
      setError('Please enter a valid repository (e.g., TejasKeerthi/ART-VAULT)');
      return;
    }

    setIsLoading(true);
    setError(null);
    setCurrentRepo(repoUrl);

    try {
      const success = await loadData(repoUrl);
      if (!success) {
        // Keep current data, error is already set
        console.warn('Analysis failed for:', repoUrl);
      }
    } finally {
      setIsLoading(false);
    }
  }, [loadData]);

  return {
    data,
    isLoading,
    refreshData,
    analyzeGitHubRepo,
    currentRepo,
    error,
  };
};
