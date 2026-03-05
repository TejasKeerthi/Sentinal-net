import { useState, useCallback } from 'react';
import type { SystemData } from '../types';
import { mockSystemData } from '../data/mockData';
import { analyzeRepository } from '../services/githubAnalyzer';

export const useSystemData = () => {
  const [data, setData] = useState<SystemData>(mockSystemData);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRepo, setCurrentRepo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * Analyze a GitHub repo directly from the browser using the public GitHub API.
   * No backend server required — NLP runs in-browser.
   */
  const analyzeGitHubRepo = useCallback(async (repoUrl: string) => {
    if (!repoUrl.trim()) {
      setError('Please enter a valid repository (e.g., TejasKeerthi/ART-VAULT)');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await analyzeRepository(repoUrl.trim());
      setData(result);
      setCurrentRepo(repoUrl.trim());
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Analysis failed';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Refresh: re-analyze the current repo, or no-op if none selected.
   */
  const refreshData = useCallback(async () => {
    if (!currentRepo) return;
    setIsLoading(true);
    setError(null);
    try {
      const result = await analyzeRepository(currentRepo);
      setData(result);
      setError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Refresh failed';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [currentRepo]);

  return {
    data,
    isLoading,
    refreshData,
    analyzeGitHubRepo,
    currentRepo,
    error,
  };
};
