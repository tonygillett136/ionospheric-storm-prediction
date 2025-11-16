import { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, Area, AreaChart } from 'recharts';
import api from '../services/api';
import './RegionalPredictions.css';

const RegionalPredictions = () => {
  const [regionalData, setRegionalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState('global');
  const [timelineData, setTimelineData] = useState({});
  const [loadingTimeline, setLoadingTimeline] = useState(false);

  useEffect(() => {
    fetchRegionalPredictions();
    // Refresh every 5 minutes
    const interval = setInterval(fetchRegionalPredictions, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedRegion && regionalData) {
      fetchTimelineForRegion(selectedRegion);
    }
  }, [selectedRegion]);

  const fetchRegionalPredictions = async () => {
    try {
      setLoading(true);
      const data = await api.getRegionalPredictions();
      setRegionalData(data);
      setError(null);
      // Fetch timeline for default region
      if (data && data.regional_predictions) {
        fetchTimelineForRegion('global');
      }
    } catch (err) {
      console.error('Error fetching regional predictions:', err);
      setError('Failed to load regional predictions');
    } finally {
      setLoading(false);
    }
  };

  const fetchTimelineForRegion = async (regionCode) => {
    if (timelineData[regionCode]) {
      return; // Already loaded
    }

    try {
      setLoadingTimeline(true);
      const data = await api.getRegionalEvolution(regionCode, { hours: 24, interval_hours: 1 });
      setTimelineData(prev => ({
        ...prev,
        [regionCode]: data
      }));
    } catch (err) {
      console.error(`Error fetching timeline for ${regionCode}:`, err);
    } finally {
      setLoadingTimeline(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    const colors = {
      'LOW': '#10b981',
      'MODERATE': '#fbbf24',
      'HIGH': '#f97316',
      'SEVERE': '#ef4444',
      'EXTREME': '#991b1b'
    };
    return colors[riskLevel] || '#6b7280';
  };

  const getRiskIcon = (riskLevel) => {
    const icons = {
      'LOW': '✓',
      'MODERATE': '⚠',
      'HIGH': '⚠',
      'SEVERE': '⚡',
      'EXTREME': '⚡'
    };
    return icons[riskLevel] || '•';
  };

  if (loading && !regionalData) {
    return (
      <div className="regional-predictions loading">
        <div className="spinner"></div>
        <p>Loading regional predictions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="regional-predictions error">
        <p>{error}</p>
        <button onClick={fetchRegionalPredictions}>Retry</button>
      </div>
    );
  }

  if (!regionalData || !regionalData.regional_predictions) {
    return null;
  }

  const { global_overview, regional_predictions, highlights } = regionalData;
  const regions = Object.values(regional_predictions);

  // Prepare data for bar chart
  const chartData = regions.map(region => ({
    name: region.region,
    tec: region.tec,
    normal: region.climatology_normal || region.tec,
    code: region.code,
    riskColor: region.risk.color
  }));

  return (
    <div className="regional-predictions">
      <div className="regional-header">
        <div className="header-content">
          <h2>🌐 Regional Ionospheric Predictions</h2>
          <div className="validation-badge">
            <span className="badge-icon">✓</span>
            <span className="badge-text">Scientifically Validated</span>
            <span className="badge-detail">90-day backtest</span>
          </div>
        </div>
        <p className="header-description">
          Geographic-specific TEC forecasts with region-adapted thresholds
        </p>
      </div>

      {/* Highlights Section */}
      {highlights && (
        <div className="highlights-section">
          <div className="highlight-card">
            <div className="highlight-icon">📍</div>
            <div className="highlight-content">
              <div className="highlight-label">Most Affected Region</div>
              <div className="highlight-value">{highlights.most_affected_name}</div>
              <div className="highlight-message">{highlights.message}</div>
            </div>
          </div>
          <div className="highlight-card">
            <div className="highlight-icon">📊</div>
            <div className="highlight-content">
              <div className="highlight-label">Highest TEC</div>
              <div className="highlight-value">{highlights.highest_tec_value} TECU</div>
              <div className="highlight-region">
                {regional_predictions[highlights.highest_tec_region]?.region}
              </div>
            </div>
          </div>
          <div className="highlight-card">
            <div className="highlight-icon">🌍</div>
            <div className="highlight-content">
              <div className="highlight-label">Global Overview</div>
              <div className="highlight-value" style={{ color: global_overview.risk.color }}>
                {global_overview.risk.level}
              </div>
              <div className="highlight-kp">Kp: {global_overview.kp_index.toFixed(1)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Regional Cards Grid */}
      <div className="regional-grid">
        {regions.map(region => (
          <div
            key={region.code}
            className={`region-card ${selectedRegion === region.code ? 'selected' : ''}`}
            onClick={() => setSelectedRegion(region.code)}
            style={{ borderLeft: `4px solid ${region.risk.color}` }}
          >
            <div className="region-card-header">
              <h3>{region.region}</h3>
              <div
                className="risk-badge"
                style={{
                  backgroundColor: region.risk.color,
                  color: 'white'
                }}
              >
                {getRiskIcon(region.risk.level)} {region.risk.level}
              </div>
            </div>

            <div className="region-stats">
              <div className="stat-item">
                <div className="stat-label">Current TEC</div>
                <div className="stat-value">{region.tec} <span className="stat-unit">TECU</span></div>
              </div>

              {region.climatology_normal && (
                <div className="stat-item">
                  <div className="stat-label">Climatology Normal</div>
                  <div className="stat-value">{region.climatology_normal} <span className="stat-unit">TECU</span></div>
                </div>
              )}

              {region.change_percent !== 0 && (
                <div className="stat-item">
                  <div className="stat-label">Change from Normal</div>
                  <div className={`stat-value ${region.change_percent > 0 ? 'positive' : 'negative'}`}>
                    {region.change_percent > 0 ? '+' : ''}{region.change_percent}%
                  </div>
                </div>
              )}
            </div>

            <div className="region-info">
              <div className="info-item">
                <span className="info-label">Latitude:</span>
                <span className="info-value">
                  {region.lat_range[0]}° to {region.lat_range[1]}°
                </span>
              </div>
              <div className="info-description">{region.description}</div>
            </div>

            <div className="region-footer">
              <div className="approach-badge">
                {region.approach}
              </div>
              <div className="severity-indicator">
                Severity: {region.risk.severity}/5
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 24-Hour Timeline Forecast */}
      {selectedRegion && timelineData[selectedRegion] && (
        <div className="timeline-section">
          <div className="timeline-header">
            <h3>📈 24-Hour TEC Forecast - {regional_predictions[selectedRegion]?.region}</h3>
            <p className="timeline-subtitle">
              Predicted TEC evolution over the next 24 hours based on climatological patterns
            </p>
          </div>

          {loadingTimeline ? (
            <div className="timeline-loading">
              <div className="spinner-small"></div>
              <span>Loading timeline...</span>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={timelineData[selectedRegion].time_series}>
                <defs>
                  <linearGradient id="tecGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={regional_predictions[selectedRegion]?.risk.color} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={regional_predictions[selectedRegion]?.risk.color} stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis
                  dataKey="hour_offset"
                  stroke="#888"
                  label={{ value: 'Hours Ahead', position: 'insideBottom', offset: -5, fill: '#888' }}
                  tickFormatter={(value) => `+${value}h`}
                />
                <YAxis
                  stroke="#888"
                  label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft', fill: '#888' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1a1a1a',
                    border: '1px solid #333',
                    borderRadius: '8px'
                  }}
                  formatter={(value, name) => {
                    if (name === 'tec') return [value.toFixed(2) + ' TECU', 'TEC'];
                    if (name === 'risk_level') return [value, 'Risk'];
                    return [value, name];
                  }}
                  labelFormatter={(hour) => `+${hour} hours`}
                />
                <Area
                  type="monotone"
                  dataKey="tec"
                  stroke={regional_predictions[selectedRegion]?.risk.color}
                  strokeWidth={3}
                  fill="url(#tecGradient)"
                  name="TEC"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}

          {/* Risk Level Timeline */}
          {timelineData[selectedRegion] && (
            <div className="risk-timeline">
              <h4>Risk Level Evolution</h4>
              <div className="risk-timeline-bars">
                {timelineData[selectedRegion].time_series.slice(0, 24).map((point, index) => {
                  const riskColors = {
                    'LOW': '#10b981',
                    'MODERATE': '#fbbf24',
                    'HIGH': '#f97316',
                    'SEVERE': '#ef4444',
                    'EXTREME': '#991b1b'
                  };
                  return (
                    <div key={index} className="risk-bar-container">
                      <div
                        className="risk-bar"
                        style={{
                          backgroundColor: riskColors[point.risk_level] || '#6b7280',
                          height: `${(point.risk_severity / 5) * 100}%`
                        }}
                        title={`${point.hour_offset}h: ${point.risk_level} (${point.tec} TECU)`}
                      />
                      {index % 3 === 0 && (
                        <span className="risk-bar-label">+{point.hour_offset}h</span>
                      )}
                    </div>
                  );
                })}
              </div>
              <div className="risk-legend">
                <span>Low</span>
                <span>Moderate</span>
                <span>High</span>
                <span>Severe</span>
                <span>Extreme</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Comparison Chart */}
      <div className="comparison-section">
        <h3>TEC Comparison Across Regions</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="name"
              stroke="#888"
              angle={-15}
              textAnchor="end"
              height={80}
            />
            <YAxis
              stroke="#888"
              label={{ value: 'TEC (TECU)', angle: -90, position: 'insideLeft', fill: '#888' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a1a',
                border: '1px solid #333',
                borderRadius: '8px'
              }}
            />
            <Legend />
            <Bar dataKey="normal" fill="#4a5568" name="Climatology Normal" />
            <Bar dataKey="tec" name="Current TEC">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.riskColor} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Scientific Validation Note */}
      <div className="validation-note">
        <div className="validation-icon">🔬</div>
        <div className="validation-text">
          <strong>ML-Enhanced Predictions:</strong> Regional forecasts now use the same ensemble ML model
          as the main dashboard, combining climatological patterns with neural network storm predictions
          for improved accuracy. Geographic-specific thresholds ensure region-adapted risk assessments.
        </div>
      </div>
    </div>
  );
};

export default RegionalPredictions;
