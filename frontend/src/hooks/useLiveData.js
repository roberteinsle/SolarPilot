/**
 * Custom Hook für Live-Daten-Polling.
 */

import { useState, useEffect, useCallback } from 'react';
import { getLiveData } from '../services/api';

/**
 * Hook für Live-Daten mit automatischem Polling.
 *
 * @param {number} intervalMs - Polling-Intervall in Millisekunden (Standard: 30000)
 * @returns {Object} { data, loading, error, lastUpdate, refetch }
 */
export const useLiveData = (intervalMs = 30000) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const result = await getLiveData();
      setData(result);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (err) {
      console.error('Fehler beim Abrufen der Live-Daten:', err);
      setError(err.message || 'Fehler beim Laden der Daten');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initiales Laden
    fetchData();

    // Polling starten
    const interval = setInterval(fetchData, intervalMs);

    // Cleanup beim Unmount
    return () => clearInterval(interval);
  }, [fetchData, intervalMs]);

  return { data, loading, error, lastUpdate, refetch: fetchData };
};
