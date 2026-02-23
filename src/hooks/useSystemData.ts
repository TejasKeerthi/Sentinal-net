import { useState, useCallback, useEffect, useRef } from 'react';
import type { SystemData } from '../types';
import { mockSystemData } from '../data/mockData';

const API_BASE_URL = 'http://localhost:8000';
const AUTO_REFRESH_INTERVAL = 30000; // 30 seconds

export const useSystemData = () => {
  const [data, setData] = useState<SystemData>(mockSystemData);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRepo, setCurrentRepo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const autoRefreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load data from API
  const loadData = useCallback(async (repoUrl?: string) => {
    try {
      const url = repoUrl 
        ? `${API_BASE_URL}/api/analyze-github?repo=${encodeURIComponent(repoUrl)}`
        : `${API_BASE_URL}/api/system-data`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const newData = await response.json();
      
      // Check if it's an error response from GitHub analyzer
      if (newData.error) {
        console.warn('GitHub API error:', newData.message);
        setError(newData.message);
        return false;
      }
      
      setData(newData);
      setError(null);
      if (repoUrl) setCurrentRepo(repoUrl);
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch data';
      console.error('Error loading data:', errorMessage);
      setError(errorMessage);
      return false;
    }
  }, []);

  // Set up auto-refresh on component mount
  useEffect(() => {
    // Load initial data
    loadData();

    // Set up auto-refresh interval
    autoRefreshIntervalRef.current = setInterval(() => {
      loadData();
    }, AUTO_REFRESH_INTERVAL);

    // Cleanup on unmount
    return () => {
      if (autoRefreshIntervalRef.current) {
        clearInterval(autoRefreshIntervalRef.current);
      }
    };
  }, [loadData]);

  // Manual refresh
  const refreshData = useCallback(async () => {
    setIsLoading(true);
    try {
      // If we have a current repo, analyze it
      if (currentRepo) {
        await loadData(currentRepo);
      } else {
        await loadData();
      }
    } finally {
      setIsLoading(false);
    }
  }, [currentRepo, loadData]);

  // Analyze GitHub repo
  const analyzeGitHubRepo = useCallback(async (repoUrl: string) => {
    setIsLoading(true);
    try {
      await loadData(repoUrl);
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
