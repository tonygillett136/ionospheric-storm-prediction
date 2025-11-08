import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import api from '../services/api';
import '../styles/ClimatologyExplorer.css';

const ClimatologyExplorer = () => {
  const [climatologyData, setClimatologyData] = useState(null);
  const [heatmapData, setHeatmapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('timeseries'); // 'timeseries', 'heatmap', 'seasonal', 'geographic'

  // User controls
  const [days, setDays] = useState(365);
  const [kpScenario, setKpScenario] = useState('moderate');
  const [selectedKpLevels, setSelectedKpLevels] = useState([2, 5, 7]); // For multi-line comparison

  // Geographic climatology state
  const [availableRegions, setAvailableRegions] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState('global');
  const [geographicData, setGeographicData] = useState(null);
  const [regionComparison, setRegionComparison] = useState(null)

  useEffect(() => {
    if (activeView === 'timeseries') {
      loadClimatologyData();
    } else if (activeView === 'heatmap' || activeView === 'seasonal') {
      loadHeatmapData();
    } else if (activeView === 'geographic') {
      loadGeographicData();
    }
  }, [days, kpScenario, activeView, selectedRegion]);

  // Load available regions on component mount
  useEffect(() => {
    loadAvailableRegions();
  }, []);

  const loadClimatologyData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.exploreClimatology({
        days,
        kp_scenario: kpScenario,
        hourly_resolution: days <= 90 // Use hourly for shorter periods
      });
      setClimatologyData(data);
    } catch (err) {
      setError(err.message || 'Failed to load climatology data');
      console.error('Error loading climatology:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadHeatmapData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getClimatologyHeatmap();
      setHeatmapData(data);
    } catch (err) {
      setError(err.message || 'Failed to load heatmap data');
      console.error('Error loading heatmap:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableRegions = async () => {
    try {
      const data = await api.getGeographicRegions();
      setAvailableRegions(data.regions || []);
    } catch (err) {
      console.error('Error loading regions:', err);
    }
  };

  const loadGeographicData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [regionData, comparison] = await Promise.all([
        api.exploreGeographicClimatology({
          region: selectedRegion,
          days,
          kp_scenario: kpScenario
        }),
        api.compareRegions({
          kp_scenario: kpScenario
        })
      ]);
      setGeographicData(regionData);
      setRegionComparison(comparison);
    } catch (err) {
      setError(err.message || 'Failed to load geographic data');
      console.error('Error loading geographic data:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = () => {
    if (!climatologyData || !climatologyData.data) return [];

    return climatologyData.data.map((point, index) => {
      const date = new Date(point.timestamp);
      return {
        index,
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        fullDate: date.toISOString(),
        tec: point.tec_mean,
        dayOfYear: point.day_of_year
      };
    });
  };

  const getSeasonalData = () => {
    if (!heatmapData) return [];

    const seasons = heatmapData.statistics?.by_season || {};
    return Object.entries(seasons).map(([season, stats]) => ({
      season: season.charAt(0).toUpperCase() + season.slice(1),
      mean: stats.mean,
      min: stats.min,
      max: stats.max,
      range: stats.max - stats.min
    }));
  };

  const getKpComparisonData = () => {
    if (!heatmapData) return [];

    // Sample every 7 days for readability
    return heatmapData.heatmap
      .filter((_, index) => index % 7 === 0)
      .map(row => {
        const result = {
          day: row.day_of_year,
          date: new Date(row.date_example).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        };
        selectedKpLevels.forEach(kp => {
          result[`Kp ${kp}`] = row.kp_values[`kp_${kp}`];
        });
        return result;
      });
  };

  const toggleKpLevel = (kp) => {
    if (selectedKpLevels.includes(kp)) {
      setSelectedKpLevels(selectedKpLevels.filter(k => k !== kp));
    } else {
      setSelectedKpLevels([...selectedKpLevels, kp].sort());
    }
  };

  const kpScenarioDescriptions = {
    quiet: 'Quiet geomagnetic conditions (Kp = 2)',
    moderate: 'Moderate conditions (Kp = 5)',
    storm: 'Storm conditions (Kp = 7)',
    current: 'Current observed Kp index'
  };

  const getKpColor = (kp) => {
    const colors = {
      0: '#4ade80', 1: '#4ade80', 2: '#86efac',
      3: '#fcd34d', 4: '#fbbf24',
      5: '#fb923c', 6: '#f97316',
      7: '#ef4444', 8: '#dc2626', 9: '#991b1b'
    };
    return colors[kp] || '#6b7280';
  };

  return (
    <div className="climatology-explorer">
      <div className="explorer-header">
        <h2>Climatology Explorer</h2>
        <p className="explorer-subtitle">
          Explore ionospheric TEC climatology based on 2015-2022 historical patterns.
          Climatology represents typical conditions for each day of the year.
        </p>
      </div>

      {/* Educational Info Box */}
      <div className="info-box">
        <h3>What is Climatology?</h3>
        <p>
          <strong>Climatology</strong> represents the long-term average conditions based on historical data.
          In our system, it captures typical Total Electron Content (TEC) patterns for each day of the year
          and different geomagnetic activity levels (Kp index).
        </p>
        <p>
          Think of it as the "climate" vs "weather" distinction: climatology tells us what's <em>typical</em>
          for a given time of year, while our neural network models predict specific <em>storm events</em>.
          Together, they form our ensemble prediction system (70% climatology + 30% neural network).
        </p>
        <div className="key-points">
          <div className="key-point">
            <strong>Seasonal Patterns:</strong> TEC varies naturally throughout the year due to solar angle and atmospheric conditions
          </div>
          <div className="key-point">
            <strong>Geomagnetic Effects:</strong> Higher Kp index (storm conditions) correlates with different TEC patterns
          </div>
          <div className="key-point">
            <strong>Predictable Baseline:</strong> Climatology provides a reliable baseline that performs well for typical conditions
          </div>
        </div>
      </div>

      {/* View Selection Tabs */}
      <div className="view-tabs">
        <button
          className={`tab ${activeView === 'timeseries' ? 'active' : ''}`}
          onClick={() => setActiveView('timeseries')}
        >
          Time Series
        </button>
        <button
          className={`tab ${activeView === 'heatmap' ? 'active' : ''}`}
          onClick={() => setActiveView('heatmap')}
        >
          Kp Comparison
        </button>
        <button
          className={`tab ${activeView === 'seasonal' ? 'active' : ''}`}
          onClick={() => setActiveView('seasonal')}
        >
          Seasonal Patterns
        </button>
        <button
          className={`tab ${activeView === 'geographic' ? 'active' : ''}`}
          onClick={() => setActiveView('geographic')}
        >
          Geographic Analysis
        </button>
      </div>

      {/* Controls */}
      {activeView === 'timeseries' && (
        <div className="controls">
          <div className="control-group">
            <label htmlFor="days">Time Range:</label>
            <select
              id="days"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
            >
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
              <option value={180}>6 months</option>
              <option value={365}>1 year</option>
              <option value={730}>2 years</option>
            </select>
          </div>

          <div className="control-group">
            <label htmlFor="kp-scenario">Kp Scenario:</label>
            <select
              id="kp-scenario"
              value={kpScenario}
              onChange={(e) => setKpScenario(e.target.value)}
            >
              <option value="quiet">Quiet (Kp = 2)</option>
              <option value="moderate">Moderate (Kp = 5)</option>
              <option value="storm">Storm (Kp = 7)</option>
              <option value="current">Current Kp</option>
            </select>
          </div>

          <div className="scenario-description">
            {kpScenarioDescriptions[kpScenario]}
          </div>
        </div>
      )}

      {activeView === 'heatmap' && (
        <div className="controls">
          <div className="kp-selector">
            <label>Select Kp Levels to Compare:</label>
            <div className="kp-buttons">
              {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(kp => (
                <button
                  key={kp}
                  className={`kp-button ${selectedKpLevels.includes(kp) ? 'selected' : ''}`}
                  style={{
                    backgroundColor: selectedKpLevels.includes(kp) ? getKpColor(kp) : '#e5e7eb',
                    color: selectedKpLevels.includes(kp) ? '#fff' : '#374151'
                  }}
                  onClick={() => toggleKpLevel(kp)}
                >
                  Kp {kp}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeView === 'geographic' && (
        <div className="controls">
          <div className="control-group">
            <label htmlFor="geographic-region">Geographic Region:</label>
            <select
              id="geographic-region"
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
            >
              {availableRegions.map(region => (
                <option key={region.code} value={region.code}>
                  {region.name} ({region.lat_range[0]}° to {region.lat_range[1]}°)
                </option>
              ))}
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="geographic-days">Time Range:</label>
            <select
              id="geographic-days"
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
            >
              <option value="7">7 days</option>
              <option value="30">30 days</option>
              <option value="90">90 days (3 months)</option>
              <option value="180">180 days (6 months)</option>
              <option value="365">365 days (1 year)</option>
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="geographic-kp">Kp Scenario:</label>
            <select
              id="geographic-kp"
              value={kpScenario}
              onChange={(e) => setKpScenario(e.target.value)}
            >
              <option value="quiet">Quiet (Kp ≈ 2)</option>
              <option value="moderate">Moderate (Kp ≈ 3)</option>
              <option value="storm">Storm (Kp ≈ 6)</option>
            </select>
          </div>
          <button onClick={loadGeographicData}>Refresh</button>
        </div>
      )}

      {/* Loading and Error States */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading climatology data...</p>
        </div>
      )}

      {error && (
        <div className="error-state">
          <p>Error: {error}</p>
          <button onClick={() => activeView === 'timeseries' ? loadClimatologyData() : loadHeatmapData()}>
            Retry
          </button>
        </div>
      )}

      {/* Chart Views */}
      {!loading && !error && (
        <>
          {activeView === 'timeseries' && climatologyData && (
            <div className="chart-section">
              <h3>Climatological TEC Forecast</h3>
              <div className="stats-row">
                <div className="stat-box">
                  <span className="stat-label">Mean TEC</span>
                  <span className="stat-value">{climatologyData.statistics.mean} TECU</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Range</span>
                  <span className="stat-value">
                    {climatologyData.statistics.min} - {climatologyData.statistics.max} TECU
                  </span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Std Dev</span>
                  <span className="stat-value">{climatologyData.statistics.std} TECU</span>
                </div>
                <div className="stat-box">
                  <span className="stat-label">Data Points</span>
                  <span className="stat-value">{climatologyData.metadata.data_points}</span>
                </div>
              </div>

              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={formatChartData()}>
                  <defs>
                    <linearGradient id="colorTec" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    interval={Math.floor(formatChartData().length / 12)}
                  />
                  <YAxis
                    label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="custom-tooltip">
                            <p className="tooltip-date">{data.date}</p>
                            <p className="tooltip-value">TEC: {data.tec} TECU</p>
                            <p className="tooltip-doy">Day of Year: {data.dayOfYear}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="tec"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#colorTec)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {activeView === 'heatmap' && heatmapData && selectedKpLevels.length > 0 && (
            <div className="chart-section">
              <h3>TEC by Kp Level Throughout the Year</h3>
              <p className="chart-description">
                Compare how TEC varies across the year for different geomagnetic activity levels.
                Higher Kp values (storm conditions) typically show different patterns than quiet conditions.
              </p>

              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={getKpComparisonData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    interval={Math.floor(getKpComparisonData().length / 12)}
                  />
                  <YAxis
                    label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip />
                  <Legend />
                  {selectedKpLevels.map(kp => (
                    <Line
                      key={kp}
                      type="monotone"
                      dataKey={`Kp ${kp}`}
                      stroke={getKpColor(kp)}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>

              {/* Kp Statistics Table */}
              <div className="kp-stats-table">
                <h4>Statistics by Kp Level</h4>
                <table>
                  <thead>
                    <tr>
                      <th>Kp Level</th>
                      <th>Mean TEC</th>
                      <th>Std Dev</th>
                      <th>Range</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedKpLevels.map(kp => {
                      const stats = heatmapData.statistics.by_kp_level[`kp_${kp}`];
                      return (
                        <tr key={kp}>
                          <td>
                            <span
                              className="kp-indicator"
                              style={{ backgroundColor: getKpColor(kp) }}
                            >
                              Kp {kp}
                            </span>
                          </td>
                          <td>{stats.mean} TECU</td>
                          <td>{stats.std} TECU</td>
                          <td>{stats.min} - {stats.max} TECU</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeView === 'seasonal' && heatmapData && (
            <div className="chart-section">
              <h3>Seasonal Patterns in Ionospheric TEC</h3>
              <p className="chart-description">
                While mean TEC values are relatively stable across seasons (averaging ~10 TECU),
                the <strong>variability</strong> and range show distinct seasonal patterns.
                This chart shows the full range of TEC values (min to max) observed in each season.
              </p>

              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={getSeasonalData()}>
                  <defs>
                    <linearGradient id="colorSeasonMax" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.2}/>
                    </linearGradient>
                    <linearGradient id="colorSeasonMin" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="season" />
                  <YAxis
                    label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }}
                    domain={[0, 20]}
                  />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="custom-tooltip">
                            <p className="tooltip-date"><strong>{data.season}</strong></p>
                            <p className="tooltip-value">Range: {data.min} - {data.max} TECU</p>
                            <p className="tooltip-value">Mean: {data.mean} TECU</p>
                            <p className="tooltip-doy">Variability: {data.range.toFixed(1)} TECU</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="max"
                    stroke="#10b981"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorSeasonMax)"
                    name="Maximum TEC"
                  />
                  <Area
                    type="monotone"
                    dataKey="mean"
                    stroke="#fbbf24"
                    strokeWidth={2}
                    fill="transparent"
                    name="Mean TEC"
                    strokeDasharray="5 5"
                  />
                  <Area
                    type="monotone"
                    dataKey="min"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorSeasonMin)"
                    name="Minimum TEC"
                  />
                </AreaChart>
              </ResponsiveContainer>

              {/* Seasonal Statistics */}
              <div className="seasonal-stats">
                {getSeasonalData().map(season => (
                  <div key={season.season} className="season-card">
                    <h4>{season.season}</h4>
                    <div className="season-stat">
                      <span className="label">Mean:</span>
                      <span className="value">{season.mean} TECU</span>
                    </div>
                    <div className="season-stat">
                      <span className="label">Range:</span>
                      <span className="value">{season.min} - {season.max} TECU</span>
                    </div>
                    <div className="season-stat">
                      <span className="label">Variability:</span>
                      <span className="value">{season.range.toFixed(1)} TECU</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="info-box" style={{ marginTop: '2rem' }}>
                <h4>Understanding Seasonal Patterns</h4>
                <p>
                  <strong>Why are the means so similar?</strong> The seasonal averages (~10 TECU)
                  are calculated across all geomagnetic conditions (Kp 0-9), which smooths out variations.
                  However, the <em>range</em> and <em>variability</em> differ significantly by season.
                </p>
                <p>
                  <strong>Key insight:</strong> Spring and Autumn show the highest TEC values (up to ~19 TECU)
                  during storm conditions, while minimum values remain relatively consistent across seasons.
                  This reflects the "equinoctial effect" where ionospheric activity peaks during equinoxes.
                </p>
              </div>
            </div>
          )}

          {activeView === 'geographic' && geographicData && regionComparison && (
            <div className="chart-section">
              <h3>Geographic Analysis: {geographicData.region.name}</h3>
              <p className="chart-description">
                {geographicData.region.description}
                <br />
                Latitude range: {geographicData.region.lat_range[0]}° to {geographicData.region.lat_range[1]}°
              </p>

              {/* Regional Forecast Time Series */}
              <div style={{ marginBottom: '3rem' }}>
                <h4>Regional TEC Forecast</h4>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={geographicData.forecast}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="tec" stroke="#3b82f6" strokeWidth={2} name="TEC" />
                  </LineChart>
                </ResponsiveContainer>
                <div className="info-box" style={{ marginTop: '1rem' }}>
                  <strong>Statistics:</strong> Mean: {geographicData.statistics.mean_tec} TECU |
                  Range: {geographicData.statistics.min_tec} - {geographicData.statistics.max_tec} TECU
                </div>
              </div>

              {/* Region Comparison */}
              <div>
                <h4>Regional Comparison</h4>
                <p className="chart-description">
                  TEC varies significantly by latitude. This chart compares all geographic regions for {regionComparison.date}.
                </p>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={regionComparison.regions}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="region" />
                    <YAxis label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="custom-tooltip">
                            <p className="tooltip-date"><strong>{data.region}</strong></p>
                            <p className="tooltip-value">TEC: {data.tec} TECU</p>
                            <p className="tooltip-doy">{data.description}</p>
                          </div>
                        );
                      }
                      return null;
                    }} />
                    <Line type="monotone" dataKey="tec" stroke="#10b981" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
                <div className="info-box" style={{ marginTop: '1rem' }}>
                  <strong>Key Insight:</strong> TEC is highest in {regionComparison.insights.highest_tec_region} regions
                  and lowest in {regionComparison.insights.lowest_tec_region} regions.
                  The difference can be up to {regionComparison.insights.tec_range} TECU.
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {/* Educational Footer */}
      <div className="explorer-footer">
        <h3>How We Use Climatology in Predictions</h3>
        <p>
          Our ensemble prediction system combines climatology with a neural network model.
          By default, predictions are weighted 70% climatology and 30% neural network,
          as validation showed this provides the most accurate forecasts.
        </p>
        <div className="footer-stats">
          <div className="footer-stat">
            <strong>Climatology Performance:</strong>
            <span>16.18 TECU RMSE on validation data</span>
          </div>
          <div className="footer-stat">
            <strong>Training Period:</strong>
            <span>2015-2022 (8 years of historical data)</span>
          </div>
          <div className="footer-stat">
            <strong>Update Frequency:</strong>
            <span>Static (pre-computed at system startup)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClimatologyExplorer;
