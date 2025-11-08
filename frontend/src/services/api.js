/**
 * API Service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1';

class APIService {
  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.websocket = null;
    this.wsCallbacks = new Set();
  }

  // REST API Methods

  async getCurrentData() {
    try {
      const response = await this.axiosInstance.get('/current');
      return response.data;
    } catch (error) {
      console.error('Error fetching current data:', error);
      throw error;
    }
  }

  async getPrediction() {
    try {
      const response = await this.axiosInstance.get('/prediction');
      return response.data;
    } catch (error) {
      console.error('Error fetching prediction:', error);
      throw error;
    }
  }

  async getEnsemblePrediction(climatologyWeight = 0.7, modelWeight = 0.3) {
    try {
      const response = await this.axiosInstance.get('/prediction/ensemble', {
        params: {
          climatology_weight: climatologyWeight,
          model_weight: modelWeight
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching ensemble prediction:', error);
      throw error;
    }
  }

  async getCurrentTEC() {
    try {
      const response = await this.axiosInstance.get('/tec/current');
      return response.data;
    } catch (error) {
      console.error('Error fetching TEC data:', error);
      throw error;
    }
  }

  async getCurrentSpaceWeather() {
    try {
      const response = await this.axiosInstance.get('/space-weather/current');
      return response.data;
    } catch (error) {
      console.error('Error fetching space weather data:', error);
      throw error;
    }
  }

  async getTrends(hours = 24) {
    try {
      const response = await this.axiosInstance.get(`/trends/${hours}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching trends:', error);
      throw error;
    }
  }

  async triggerDataUpdate() {
    try {
      const response = await this.axiosInstance.post('/update/data');
      return response.data;
    } catch (error) {
      console.error('Error triggering data update:', error);
      throw error;
    }
  }

  async triggerPredictionUpdate() {
    try {
      const response = await this.axiosInstance.post('/update/prediction');
      return response.data;
    } catch (error) {
      console.error('Error triggering prediction update:', error);
      throw error;
    }
  }

  async getHealth() {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }

  async exploreClimatology(params = {}) {
    try {
      const response = await this.axiosInstance.get('/climatology/explore', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching climatology data:', error);
      throw error;
    }
  }

  async getClimatologyHeatmap() {
    try {
      const response = await this.axiosInstance.get('/climatology/heatmap');
      return response.data;
    } catch (error) {
      console.error('Error fetching climatology heatmap:', error);
      throw error;
    }
  }

  async getGeographicRegions() {
    try {
      const response = await this.axiosInstance.get('/climatology/regions');
      return response.data;
    } catch (error) {
      console.error('Error fetching geographic regions:', error);
      throw error;
    }
  }

  async exploreGeographicClimatology(params = {}) {
    try {
      const response = await this.axiosInstance.get('/climatology/geographic/explore', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching geographic climatology data:', error);
      throw error;
    }
  }

  async compareRegions(params = {}) {
    try {
      const response = await this.axiosInstance.get('/climatology/geographic/compare', { params });
      return response.data;
    } catch (error) {
      console.error('Error comparing regions:', error);
      throw error;
    }
  }

  // Regional Prediction API
  async getRegionalPredictions() {
    try {
      const response = await this.axiosInstance.get('/prediction/regional');
      return response.data;
    } catch (error) {
      console.error('Error fetching regional predictions:', error);
      throw error;
    }
  }

  async getRegionalEvolution(regionCode, params = {}) {
    try {
      const response = await this.axiosInstance.get(`/prediction/regional/${regionCode}/evolution`, { params });
      return response.data;
    } catch (error) {
      console.error(`Error fetching evolution for region ${regionCode}:`, error);
      throw error;
    }
  }

  async getStormGallery() {
    try {
      const response = await this.axiosInstance.get('/storms/gallery');
      return response.data;
    } catch (error) {
      console.error('Error fetching storm gallery:', error);
      throw error;
    }
  }

  async getStormDetails(stormId) {
    try {
      const response = await this.axiosInstance.get(`/storms/${stormId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching storm ${stormId} details:`, error);
      throw error;
    }
  }

  // Recent Storm Performance API
  async getRecentStorms(params = {}) {
    try {
      // Use longer timeout for performance analysis (up to 2 minutes)
      const timeout = params.analyze_performance ? 120000 : 10000;
      const response = await this.axiosInstance.get('/storms/recent', {
        params,
        timeout
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recent storms:', error);
      throw error;
    }
  }

  async getStormPerformance(stormId, modelVersion = 'v2') {
    try {
      // Use longer timeout for performance analysis (up to 1 minute)
      const response = await this.axiosInstance.get(`/storms/recent/${stormId}/performance`, {
        params: { model_version: modelVersion },
        timeout: 60000
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching performance for storm ${stormId}:`, error);
      throw error;
    }
  }

  // Science Guide API
  async getScienceGuideChapters() {
    try {
      const response = await this.axiosInstance.get('/science-guide/chapters');
      return response.data;
    } catch (error) {
      console.error('Error fetching science guide chapters:', error);
      throw error;
    }
  }

  async getScienceGuideChapter(chapterId) {
    try {
      const response = await this.axiosInstance.get(`/science-guide/chapters/${chapterId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching science guide chapter ${chapterId}:`, error);
      throw error;
    }
  }

  // Generic HTTP methods for custom endpoints
  async get(endpoint) {
    try {
      const response = await this.axiosInstance.get(endpoint);
      return response.data;
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      throw error;
    }
  }

  async post(endpoint, data, config = {}) {
    try {
      // For backtest endpoint, use longer timeout (2 minutes)
      const timeout = endpoint.includes('/backtest/') ? 120000 : 10000;
      const response = await this.axiosInstance.post(endpoint, data, {
        timeout,
        ...config
      });
      return response.data;
    } catch (error) {
      console.error(`Error posting to ${endpoint}:`, error);
      throw error;
    }
  }

  // WebSocket Methods

  connectWebSocket(onMessage) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    this.websocket = new WebSocket(`${WS_BASE_URL}/ws`);

    this.websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);

        // Call all registered callbacks
        this.wsCallbacks.forEach(callback => callback(data));
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.websocket.onclose = () => {
      console.log('WebSocket disconnected. Reconnecting in 5 seconds...');
      setTimeout(() => this.connectWebSocket(onMessage), 5000);
    };
  }

  disconnectWebSocket() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  registerWSCallback(callback) {
    this.wsCallbacks.add(callback);
  }

  unregisterWSCallback(callback) {
    this.wsCallbacks.delete(callback);
  }

  sendWSMessage(message) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    }
  }
}

export default new APIService();
