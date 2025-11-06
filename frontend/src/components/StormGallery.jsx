import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import api from '../services/api';
import '../styles/StormGallery.css';

const StormGallery = () => {
  const [storms, setStorms] = useState([]);
  const [selectedStorm, setSelectedStorm] = useState(null);
  const [stormDetails, setStormDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadStormGallery();
  }, []);

  const loadStormGallery = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStormGallery();
      setStorms(data.storms || []);
    } catch (err) {
      setError(err.message || 'Failed to load storm gallery');
      console.error('Error loading storms:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStormDetails = async (stormId) => {
    setDetailsLoading(true);
    try {
      const data = await api.getStormDetails(stormId);
      setStormDetails(data);
    } catch (err) {
      console.error(`Error loading storm ${stormId}:`, err);
      setStormDetails({ error: err.message });
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleStormClick = (storm) => {
    setSelectedStorm(storm);
    setStormDetails(null);
    loadStormDetails(storm.id);
  };

  const getSeverityColor = (severity) => {
    const level = severity.split(' - ')[0];
    const colors = {
      'G1': '#4ade80',
      'G2': '#fbbf24',
      'G3': '#fb923c',
      'G4': '#ef4444',
      'G5': '#dc2626'
    };
    return colors[level] || '#6b7280';
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatChartData = () => {
    if (!stormDetails || !stormDetails.measurements) return [];

    return stormDetails.measurements.map(m => ({
      time: new Date(m.timestamp).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit'
      }),
      kp: m.kp_index,
      tec: m.tec_mean,
      solarWind: m.solar_wind_speed,
      imfBz: m.imf_bz
    }));
  };

  if (loading) {
    return (
      <div className="storm-gallery loading">
        <div className="spinner"></div>
        <p>Loading historical storms...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="storm-gallery error">
        <p>Error: {error}</p>
        <button onClick={loadStormGallery}>Retry</button>
      </div>
    );
  }

  return (
    <div className="storm-gallery">
      <div className="gallery-header">
        <h2>Historical Storm Gallery</h2>
        <p className="gallery-subtitle">
          Explore major geomagnetic storms from 2015-2025 with actual measurements from our NASA OMNI database.
          Click any storm to see detailed data and real-world impacts.
        </p>
      </div>

      {!selectedStorm ? (
        /* Gallery Grid View */
        <div className="storm-grid">
          {storms.map(storm => (
            <div
              key={storm.id}
              className="storm-card"
              onClick={() => handleStormClick(storm)}
              style={{ borderLeftColor: getSeverityColor(storm.severity) }}
            >
              <div className="storm-header">
                <h3>{storm.name}</h3>
                <span
                  className="severity-badge"
                  style={{ backgroundColor: getSeverityColor(storm.severity) }}
                >
                  {storm.severity}
                </span>
              </div>

              <div className="storm-date">
                {formatDate(storm.date_start)}
                {storm.date_start !== storm.date_end && ` - ${formatDate(storm.date_end)}`}
              </div>

              <p className="storm-description">{storm.description}</p>

              <div className="storm-stats">
                <div className="stat">
                  <span className="stat-label">Max Kp</span>
                  <span className="stat-value">{storm.max_kp}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Category</span>
                  <span className="stat-value">{storm.category.replace('_', ' ')}</span>
                </div>
              </div>

              {storm.notable && (
                <div className="notable-badge">⭐ Notable Event</div>
              )}
            </div>
          ))}
        </div>
      ) : (
        /* Detailed Storm View */
        <div className="storm-details">
          <button
            className="back-button"
            onClick={() => setSelectedStorm(null)}
          >
            ← Back to Gallery
          </button>

          <div className="details-header">
            <div>
              <h2>{selectedStorm.name}</h2>
              <div className="details-date">
                {formatDate(selectedStorm.date_start)}
                {selectedStorm.date_start !== selectedStorm.date_end &&
                  ` - ${formatDate(selectedStorm.date_end)}`
                }
              </div>
            </div>
            <span
              className="severity-badge large"
              style={{ backgroundColor: getSeverityColor(selectedStorm.severity) }}
            >
              {selectedStorm.severity}
            </span>
          </div>

          <div className="details-content">
            <div className="details-section">
              <h3>Overview</h3>
              <p>{selectedStorm.description}</p>
            </div>

            <div className="details-section">
              <h3>Scientific Context</h3>
              <p>{selectedStorm.scientific_context}</p>
            </div>

            <div className="details-section">
              <h3>Real-World Impacts</h3>
              <ul className="impacts-list">
                {selectedStorm.impacts.map((impact, idx) => (
                  <li key={idx}>{impact}</li>
                ))}
              </ul>
            </div>

            {selectedStorm.noaa_report_url && (
              <div className="details-section">
                <a
                  href={selectedStorm.noaa_report_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="external-link"
                >
                  View NOAA Official Report →
                </a>
              </div>
            )}

            {detailsLoading && (
              <div className="loading-indicator">
                <div className="spinner-small"></div>
                <p>Loading actual measurements...</p>
              </div>
            )}

            {stormDetails && !stormDetails.error && (
              <div className="measurements-section">
                <h3>Actual Measurements from NASA OMNI Database</h3>

                {stormDetails.statistics && (
                  <div className="stats-grid">
                    <div className="stat-card">
                      <span className="stat-label">Maximum Kp</span>
                      <span className="stat-value">{stormDetails.statistics.max_kp}</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Average Kp</span>
                      <span className="stat-value">{stormDetails.statistics.avg_kp}</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Maximum TEC</span>
                      <span className="stat-value">{stormDetails.statistics.max_tec?.toFixed(1)} TECU</span>
                    </div>
                    <div className="stat-card">
                      <span className="stat-label">Duration</span>
                      <span className="stat-value">{stormDetails.statistics.duration_hours}h</span>
                    </div>
                  </div>
                )}

                {stormDetails.measurements && stormDetails.measurements.length > 0 ? (
                  <>
                    <h4>Kp Index Evolution</h4>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={formatChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} />
                        <YAxis
                          label={{ value: 'Kp Index', angle: -90, position: 'insideLeft' }}
                          domain={[0, 9]}
                        />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="kp"
                          stroke="#ef4444"
                          strokeWidth={2}
                          name="Kp Index"
                        />
                      </LineChart>
                    </ResponsiveContainer>

                    <h4>TEC Response</h4>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={formatChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} />
                        <YAxis
                          label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="tec"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          name="TEC Mean"
                        />
                      </LineChart>
                    </ResponsiveContainer>

                    <h4>Solar Wind Speed</h4>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={formatChartData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="time" angle={-45} textAnchor="end" height={80} />
                        <YAxis
                          label={{ value: 'Speed (km/s)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="solarWind"
                          stroke="#10b981"
                          strokeWidth={2}
                          name="Solar Wind Speed"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </>
                ) : (
                  <p className="no-data">No measurement data available for this period in our database.</p>
                )}
              </div>
            )}

            {stormDetails && stormDetails.error && (
              <div className="error-box">
                <p>Could not load measurements: {stormDetails.error}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StormGallery;
