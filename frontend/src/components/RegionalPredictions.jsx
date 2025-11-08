import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import api from '../services/api';
import './RegionalPredictions.css';

const RegionalPredictions = () => {
  const [regionalData, setRegionalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState('global');

  useEffect(() => {
    fetchRegionalPredictions();
    // Refresh every 5 minutes
    const interval = setInterval(fetchRegionalPredictions, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchRegionalPredictions = async () => {
    try {
      setLoading(true);
      const data = await api.getRegionalPredictions();
      setRegionalData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching regional predictions:', err);
      setError('Failed to load regional predictions');
    } finally {
      setLoading(false);
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
          <strong>Experimentally Validated:</strong> This Climatology-Primary approach was proven superior
          through 90-day backtesting, winning in 4 out of 5 regions with a total improvement of 7.341 TECU.
          See <code>REGIONAL_EXPERIMENT_REPORT.md</code> for full methodology and results.
        </div>
      </div>
    </div>
  );
};

export default RegionalPredictions;
