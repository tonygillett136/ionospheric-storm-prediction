import React, { useState, useEffect } from 'react';
import { ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import API from '../services/api';
import '../styles/RecentStormPerformance.css';

const RecentStormPerformance = () => {
  const [storms, setStorms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [daysBack, setDaysBack] = useState(90);
  const [analyzePerformance, setAnalyzePerformance] = useState(false);
  const [selectedStorm, setSelectedStorm] = useState(null);
  const [performanceDetails, setPerformanceDetails] = useState(null);
  const [loadingPerformance, setLoadingPerformance] = useState(false);
  const [catalog, setCatalog] = useState(null);

  useEffect(() => {
    loadStorms();
  }, [daysBack, analyzePerformance]);

  const loadStorms = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await API.getRecentStorms({
        days_back: daysBack,
        kp_threshold: 5.0,
        analyze_performance: analyzePerformance
      });

      setCatalog(data);
      // Sort storms by start time, latest first
      const sortedStorms = (data.storms || []).sort((a, b) => {
        return new Date(b.storm_info.start_time) - new Date(a.storm_info.start_time);
      });
      setStorms(sortedStorms);
    } catch (err) {
      setError(err.message || 'Failed to load storms');
    } finally {
      setLoading(false);
    }
  };

  const handleStormClick = async (storm) => {
    if (selectedStorm && selectedStorm.storm_info && selectedStorm.storm_info.storm_id === storm.storm_info.storm_id) {
      setSelectedStorm(null);
      setPerformanceDetails(null);
      return;
    }

    setSelectedStorm(storm);
    setPerformanceDetails(null);  // Clear previous details

    // Always fetch individual performance details to get measurements for chart
    try {
      setLoadingPerformance(true);
      const perfData = await API.getStormPerformance(storm.storm_info.storm_id);
      setPerformanceDetails(perfData);
    } catch (err) {
      console.error('Error loading performance:', err);
      // Fall back to storm data if available (without chart)
      setPerformanceDetails(storm);
    } finally {
      setLoadingPerformance(false);
    }
  };

  const getSeverityColor = (gScale) => {
    const colors = {
      'G1': '#fbbf24',  // yellow
      'G2': '#fb923c',  // orange
      'G3': '#f97316',  // deep orange
      'G4': '#ef4444',  // red
      'G5': '#dc2626'   // deep red
    };
    return colors[gScale] || '#9ca3af';
  };

  const getSeverityDescription = (gScale) => {
    const descriptions = {
      'G1': 'Minor - Weak power grid fluctuations, minor aurora at high latitudes',
      'G2': 'Moderate - High-latitude power systems affected, aurora visible in northern US',
      'G3': 'Strong - Voltage control problems, aurora at mid-latitudes, satellite issues',
      'G4': 'Severe - Widespread voltage problems, aurora at lower latitudes, GPS errors',
      'G5': 'Extreme - Complete power grid failures possible, aurora visible near equator'
    };
    return descriptions[gScale] || 'Unknown severity level';
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && storms.length === 0) {
    return (
      <div className="recent-storm-performance">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading recent storms...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recent-storm-performance">
      <div className="header-section">
        <h2>📊 Recent Storm Performance Tracker</h2>
        <p className="subtitle">
          Monitor recent geomagnetic storms and evaluate model prediction accuracy
        </p>
      </div>

      <div className="controls-section">
        <div className="control-group">
          <label htmlFor="days-back">Time Period:</label>
          <select
            id="days-back"
            value={daysBack}
            onChange={(e) => setDaysBack(Number(e.target.value))}
            className="control-select"
          >
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={180}>Last 6 months</option>
            <option value={365}>Last year</option>
          </select>
        </div>

        <div className="control-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={analyzePerformance}
              onChange={(e) => setAnalyzePerformance(e.target.checked)}
            />
            <span>Analyse model performance (slower)</span>
          </label>
        </div>

        <button onClick={loadStorms} className="refresh-button" disabled={loading}>
          {loading ? 'Loading...' : '↻ Refresh'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {catalog && (
        <div className="summary-section">
          <div className="summary-card">
            <div className="summary-stat">
              <span className="stat-value">{catalog.storm_count}</span>
              <span className="stat-label">Total Storms</span>
            </div>
            <div className="summary-stat">
              <span className="stat-value">{Math.round(catalog.statistics.avg_storm_duration_hours)}h</span>
              <span className="stat-label">Avg Duration</span>
            </div>
            <div className="summary-stat">
              <span className="stat-value">{catalog.statistics.strongest_storm.g_scale}</span>
              <span className="stat-label">Strongest</span>
            </div>
          </div>

          <div className="severity-distribution">
            <h4>Severity Distribution</h4>
            <div className="severity-bars">
              {Object.entries(catalog.severity_distribution)
                .sort((a, b) => a[0].localeCompare(b[0]))  // Sort G1 to G5
                .map(([scale, count]) => (
                  <div key={scale} className="severity-bar-item">
                    <span className="severity-label" title={getSeverityDescription(scale)}>
                      {scale}
                    </span>
                    <div className="severity-bar-track">
                      <div
                        className="severity-bar-fill"
                        style={{
                          width: `${(count / catalog.storm_count) * 100}%`,
                          backgroundColor: getSeverityColor(scale)
                        }}
                        title={getSeverityDescription(scale)}
                      />
                    </div>
                    <span className="severity-count">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      <div className="storms-table-container">
        <table className="storms-table">
          <thead>
            <tr>
              <th>Start Time</th>
              <th>Severity</th>
              <th>Duration</th>
              <th>Peak Kp</th>
              <th>Avg TEC</th>
              {analyzePerformance && <th>Model Detected?</th>}
              {analyzePerformance && <th>Lead Time</th>}
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {storms.map((storm) => {
              const stormInfo = storm.storm_info;
              const isSelected = selectedStorm && selectedStorm.storm_info.storm_id === stormInfo.storm_id;

              return (
                <React.Fragment key={stormInfo.storm_id}>
                  <tr
                    className={`storm-row ${isSelected ? 'selected' : ''}`}
                    onClick={() => handleStormClick(storm)}
                  >
                    <td>{formatDate(stormInfo.start_time)}</td>
                    <td>
                      <span
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(stormInfo.g_scale) }}
                        title={getSeverityDescription(stormInfo.g_scale)}
                      >
                        {stormInfo.g_scale}
                      </span>
                    </td>
                    <td>{stormInfo.duration_hours}h</td>
                    <td>{stormInfo.peak_kp.toFixed(1)}</td>
                    <td>{stormInfo.avg_tec.toFixed(1)} TECU</td>
                    {analyzePerformance && (
                      <td>
                        {loading ? (
                          <span style={{ fontStyle: 'italic', color: '#94a3b8' }}>Calculating...</span>
                        ) : storm.model_performance?.storm_detected !== null ? (
                          storm.model_performance?.storm_detected ? '✓ Yes' : '✗ No'
                        ) : '-'}
                      </td>
                    )}
                    {analyzePerformance && (
                      <td>
                        {loading ? (
                          <span style={{ fontStyle: 'italic', color: '#94a3b8' }}>Calculating...</span>
                        ) : storm.model_performance?.detection_lead_hours ? (
                          `${storm.model_performance.detection_lead_hours}h`
                        ) : '-'}
                      </td>
                    )}
                    <td>
                      <button className="details-button">
                        {isSelected ? '▼' : '▶'}
                      </button>
                    </td>
                  </tr>

                  {isSelected && (
                    <tr className="detail-row">
                      <td colSpan={analyzePerformance ? 8 : 6}>
                        <div className="detail-content">
                          {loadingPerformance ? (
                            <div className="loading-message">Loading performance data...</div>
                          ) : (
                            <>
                              <h4>Storm Details</h4>
                              <div className="detail-grid">
                                <div className="detail-item">
                                  <strong>Storm ID:</strong> {stormInfo.storm_id}
                                </div>
                                <div className="detail-item">
                                  <strong>End Time:</strong> {formatDate(stormInfo.end_time)}
                                </div>
                                <div className="detail-item">
                                  <strong>Peak Time:</strong> {formatDate(stormInfo.peak_time)}
                                </div>
                                <div className="detail-item">
                                  <strong>Classification:</strong> {stormInfo.severity_name}
                                </div>
                                <div className="detail-item">
                                  <strong>Max TEC:</strong> {stormInfo.max_tec.toFixed(2)} TECU
                                </div>
                              </div>

                              {(performanceDetails?.model_performance || storm.model_performance) && (
                                <>
                                  <h4>Model Performance</h4>
                                  <div className="performance-grid">
                                    {(() => {
                                      const perf = performanceDetails?.model_performance || storm.model_performance;
                                      return (
                                        <>
                                          <div className="perf-item">
                                            <strong>Storm Detected:</strong>
                                            <span className={perf.storm_detected ? 'success' : 'failure'}>
                                              {perf.storm_detected ? '✓ Yes' : '✗ No'}
                                            </span>
                                          </div>
                                          {perf.detection_lead_hours && (
                                            <div className="perf-item">
                                              <strong>Detection Lead Time:</strong>
                                              <span>{perf.detection_lead_hours} hours in advance</span>
                                            </div>
                                          )}
                                          {perf.storm_rmse && (
                                            <div className="perf-item">
                                              <strong>Prediction RMSE:</strong>
                                              <span>{perf.storm_rmse}%</span>
                                            </div>
                                          )}
                                          {perf.detection_rate !== null && (
                                            <div className="perf-item">
                                              <strong>Detection Rate:</strong>
                                              <span>{perf.detection_rate}%</span>
                                            </div>
                                          )}
                                        </>
                                      );
                                    })()}
                                  </div>
                                </>
                              )}

                              {/* Storm Context Chart */}
                              {performanceDetails?.measurements && performanceDetails.measurements.length > 0 && (() => {
                                const stormStartTime = new Date(stormInfo.start_time).getTime();
                                const stormEndTime = new Date(stormInfo.end_time).getTime();

                                // Find max Kp for scaling the storm indicator
                                const maxKp = Math.max(...performanceDetails.measurements.map(m => m.kp_index));

                                // Find storm start and end indices
                                let stormStartIdx = -1;
                                let stormEndIdx = -1;
                                let minStartDiff = Infinity;
                                let minEndDiff = Infinity;

                                const chartData = performanceDetails.measurements.map((m, idx) => {
                                  const mTime = new Date(m.timestamp).getTime();

                                  // Find closest point to storm start
                                  const startDiff = Math.abs(mTime - stormStartTime);
                                  if (startDiff < minStartDiff) {
                                    minStartDiff = startDiff;
                                    stormStartIdx = idx;
                                  }

                                  // Find closest point to storm end
                                  const endDiff = Math.abs(mTime - stormEndTime);
                                  if (endDiff < minEndDiff) {
                                    minEndDiff = endDiff;
                                    stormEndIdx = idx;
                                  }

                                  return {
                                    ...m,
                                    index: idx,
                                    time: new Date(m.timestamp).toLocaleString('en-GB', {
                                      month: 'short',
                                      day: 'numeric',
                                      hour: '2-digit',
                                      minute: '2-digit',
                                      hour12: false  // Use 24-hour format
                                    }).replace(',', ''),  // Remove comma between date and time
                                    stormStartMarker: null,  // Will be set below
                                    stormEndMarker: null     // Will be set below
                                  };
                                });

                                // Mark only the start and end points
                                if (stormStartIdx >= 0) {
                                  chartData[stormStartIdx].stormStartMarker = maxKp;
                                }
                                if (stormEndIdx >= 0 && stormEndIdx !== stormStartIdx) {
                                  chartData[stormEndIdx].stormEndMarker = maxKp;
                                }

                                return (
                                  <>
                                    <h4>Storm Evolution</h4>
                                    <div style={{ marginBottom: '0.5rem', padding: '0.5rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '4px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                                      <span style={{ color: '#ef4444', fontWeight: 'bold' }}>⚡ Storm Period:</span>{' '}
                                      <span style={{ color: '#e2e8f0' }}>
                                        {formatDate(stormInfo.start_time)} → {formatDate(stormInfo.end_time)}
                                      </span>
                                      <span style={{ color: '#94a3b8', marginLeft: '1rem' }}>
                                        ({stormInfo.duration_hours} hours)
                                      </span>
                                    </div>
                                    <div style={{ marginBottom: '0.5rem', padding: '0.25rem 0.5rem', background: 'rgba(100, 116, 139, 0.1)', borderRadius: '4px', fontSize: '0.85rem', color: '#94a3b8' }}>
                                      Chart shows storm period with build-up and recovery phases (storm occupies ~50% of timeline)
                                    </div>
                                    <div className="chart-container">
                                      <ResponsiveContainer width="100%" height={300}>
                                        <ComposedChart data={chartData}>
                                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.2)" />
                                          <XAxis
                                            dataKey="time"
                                            stroke="#94a3b8"
                                            tick={{ fill: '#94a3b8', fontSize: 11 }}
                                            angle={-45}
                                            textAnchor="end"
                                            height={80}
                                          />
                                          <YAxis
                                            yAxisId="left"
                                            stroke="#fbbf24"
                                            tick={{ fill: '#94a3b8', fontSize: 12 }}
                                            label={{ value: 'Kp Index', angle: -90, position: 'insideLeft', fill: '#fbbf24' }}
                                          />
                                          <YAxis
                                            yAxisId="right"
                                            orientation="right"
                                            stroke="#3b82f6"
                                            tick={{ fill: '#94a3b8', fontSize: 12 }}
                                            label={{ value: 'TEC (TECU)', angle: 90, position: 'insideRight', fill: '#3b82f6' }}
                                          />
                                          <Tooltip
                                            contentStyle={{
                                              backgroundColor: 'rgba(15, 23, 42, 0.95)',
                                              border: '1px solid rgba(100, 116, 139, 0.3)',
                                              borderRadius: '8px',
                                              color: '#e2e8f0'
                                            }}
                                          />
                                          <Legend
                                            wrapperStyle={{ color: '#cbd5e1' }}
                                          />
                                          {/* Bar markers for storm start and end */}
                                          <Bar
                                            yAxisId="left"
                                            dataKey="stormStartMarker"
                                            fill="#ef4444"
                                            fillOpacity={0.6}
                                            name="⚡ Storm Start"
                                            barSize={4}
                                          />
                                          <Bar
                                            yAxisId="left"
                                            dataKey="stormEndMarker"
                                            fill="#10b981"
                                            fillOpacity={0.6}
                                            name="Storm End ✓"
                                            barSize={4}
                                          />
                                          <Line
                                            yAxisId="left"
                                            type="monotone"
                                            dataKey="kp_index"
                                            stroke="#fbbf24"
                                            strokeWidth={2}
                                            name="Kp Index"
                                            dot={false}
                                          />
                                          <Line
                                            yAxisId="right"
                                            type="monotone"
                                            dataKey="tec_mean"
                                            stroke="#3b82f6"
                                            strokeWidth={2}
                                            name="TEC"
                                            dot={false}
                                          />
                                        </ComposedChart>
                                      </ResponsiveContainer>
                                    </div>
                                  </>
                                );
                              })()}
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>

        {storms.length === 0 && !loading && (
          <div className="no-data-message">
            No storms detected in the selected time period.
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentStormPerformance;
