/**
 * API-Client für SolarPilot Backend.
 */

import axios from 'axios';

// API-Basis-URL aus Umgebungsvariable (wird beim Build gesetzt)
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Holt aktuelle Live-Daten.
 * @returns {Promise<Object>} Live-Daten
 */
export const getLiveData = async () => {
  const response = await apiClient.get('/live');
  return response.data;
};

/**
 * Holt Health-Status.
 * @returns {Promise<Object>} Health-Status
 */
export const getHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export default apiClient;
