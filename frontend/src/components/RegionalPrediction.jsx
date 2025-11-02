/**
 * Regional Prediction Component
 * Location-specific ionospheric storm predictions
 */
import React, { useState, useEffect } from 'react';

const RegionalPrediction = () => {
  const [latitude, setLatitude] = useState(45.0);
  const [longitude, setLongitude] = useState(-75.0);
  const [regionalData, setRegionalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Preset locations
  const presetLocations = [
    { name: 'New York, USA', lat: 40.7, lon: -74.0 },
    { name: 'London, UK', lat: 51.5, lon: -0.1 },
    { name: 'Tokyo, Japan', lat: 35.7, lon: 139.7 },
    { name: 'Sydney, Australia', lat: -33.9, lon: 151.2 },
    { name: 'Reykjavik, Iceland (Auroral)', lat: 64.1, lon: -21.9 },
    { name: 'Singapore (Equatorial)', lat: 1.3, lon: 103.8 },
    { name: 'Fairbanks, Alaska (Polar)', lat: 64.8, lon: -147.7 },
    { name: 'São Paulo, Brazil', lat: -23.5, lon: -46.6 },
  ];

  useEffect(() => {
    fetchRegionalPrediction();
  }, [latitude, longitude]);

  const fetchRegionalPrediction = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(
        `http://localhost:8000/api/v1/prediction/location?latitude=${latitude}&longitude=${longitude}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch regional prediction');
      }

      const data = await response.json();
      setRegionalData(data);
    } catch (err) {
      console.error('Error fetching regional prediction:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const selectPresetLocation = (location) => {
    setLatitude(location.lat);
    setLongitude(location.lon);
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low':
        return '#4ade80';
      case 'moderate':
        return '#facc15';
      case 'elevated':
        return '#fb923c';
      case 'high':
        return '#f87171';
      case 'severe':
        return '#dc2626';
      default:
        return '#6b7280';
    }
  };

  if (loading && !regionalData) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255,255,255,0.6)' }}>
        Loading regional prediction...
      </div>
    );
  }

  return (
    <div
      style={{
        background: 'rgba(0, 20, 40, 0.6)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(74, 144, 226, 0.3)',
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
          Regional Storm Prediction
        </h3>
        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.5' }}>
          Get location-specific predictions adjusted for regional ionospheric conditions and latitude effects.
        </p>
      </div>

      {/* Location Input */}
      <div
        style={{
          background: 'rgba(20, 30, 50, 0.5)',
          borderRadius: '12px',
          padding: '20px',
          marginBottom: '20px'
        }}
      >
        <h4 style={{ fontSize: '14px', marginBottom: '12px', fontWeight: '600' }}>Select Location</h4>

        {/* Preset Locations */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '8px', display: 'block' }}>
            Quick Select:
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {presetLocations.map((loc, idx) => (
              <button
                key={idx}
                onClick={() => selectPresetLocation(loc)}
                style={{
                  padding: '6px 12px',
                  background: latitude === loc.lat && longitude === loc.lon
                    ? 'rgba(74, 144, 226, 0.3)'
                    : 'rgba(0, 20, 40, 0.6)',
                  border: latitude === loc.lat && longitude === loc.lon
                    ? '1px solid #4a90e2'
                    : '1px solid rgba(74, 144, 226, 0.2)',
                  borderRadius: '6px',
                  color: '#fff',
                  fontSize: '11px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                {loc.name}
              </button>
            ))}
          </div>
        </div>

        {/* Manual Input */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <label style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '6px', display: 'block' }}>
              Latitude (-90 to 90):
            </label>
            <input
              type="number"
              value={latitude}
              onChange={(e) => setLatitude(parseFloat(e.target.value))}
              min="-90"
              max="90"
              step="0.1"
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(0, 20, 40, 0.6)',
                border: '1px solid rgba(74, 144, 226, 0.3)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '13px'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '6px', display: 'block' }}>
              Longitude (-180 to 180):
            </label>
            <input
              type="number"
              value={longitude}
              onChange={(e) => setLongitude(parseFloat(e.target.value))}
              min="-180"
              max="180"
              step="0.1"
              style={{
                width: '100%',
                padding: '8px',
                background: 'rgba(0, 20, 40, 0.6)',
                border: '1px solid rgba(74, 144, 226, 0.3)',
                borderRadius: '6px',
                color: '#fff',
                fontSize: '13px'
              }}
            />
          </div>
        </div>

        <button
          onClick={fetchRegionalPrediction}
          disabled={loading}
          style={{
            marginTop: '12px',
            padding: '8px 16px',
            background: 'linear-gradient(90deg, #4a90e2, #50e3c2)',
            border: 'none',
            borderRadius: '6px',
            color: '#fff',
            fontSize: '13px',
            fontWeight: 'bold',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? 'Updating...' : 'Update Prediction'}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div
          style={{
            padding: '14px',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            marginBottom: '20px',
            color: '#f87171'
          }}
        >
          Error: {error}
        </div>
      )}

      {/* Regional Prediction Results */}
      {regionalData && (
        <>
          {/* Location Info */}
          <div
            style={{
              background: 'rgba(20, 30, 50, 0.5)',
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '20px'
            }}
          >
            <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '8px' }}>
              📍 {regionalData.location.region}
            </div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
              Lat: {regionalData.location.latitude}°, Lon: {regionalData.location.longitude}°
            </div>
          </div>

          {/* Prediction Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '20px' }}>
            {/* 24h Regional Prediction */}
            <div
              style={{
                background: 'rgba(0, 20, 40, 0.4)',
                borderRadius: '12px',
                padding: '20px',
                border: `2px solid ${getRiskColor(regionalData.regional_prediction.risk_level_24h)}40`
              }}
            >
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)', marginBottom: '8px' }}>
                24-Hour Regional Forecast
              </div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: getRiskColor(regionalData.regional_prediction.risk_level_24h), marginBottom: '8px' }}>
                {regionalData.regional_prediction.storm_probability_24h}%
              </div>
              <div
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  background: `${getRiskColor(regionalData.regional_prediction.risk_level_24h)}15`,
                  border: `1.5px solid ${getRiskColor(regionalData.regional_prediction.risk_level_24h)}`,
                  fontSize: '11px',
                  fontWeight: 'bold',
                  textTransform: 'uppercase',
                  textAlign: 'center',
                  color: getRiskColor(regionalData.regional_prediction.risk_level_24h)
                }}
              >
                {regionalData.regional_prediction.risk_level_24h} Risk
              </div>
            </div>

            {/* 48h Regional Prediction */}
            <div
              style={{
                background: 'rgba(0, 20, 40, 0.4)',
                borderRadius: '12px',
                padding: '20px',
                border: `2px dashed ${getRiskColor(regionalData.regional_prediction.risk_level_48h)}40`
              }}
            >
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)', marginBottom: '8px' }}>
                48-Hour Regional Forecast
              </div>
              <div style={{ fontSize: '36px', fontWeight: 'bold', color: getRiskColor(regionalData.regional_prediction.risk_level_48h), marginBottom: '8px' }}>
                {regionalData.regional_prediction.storm_probability_48h}%
              </div>
              <div
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  background: `${getRiskColor(regionalData.regional_prediction.risk_level_48h)}15`,
                  border: `1.5px solid ${getRiskColor(regionalData.regional_prediction.risk_level_48h)}`,
                  fontSize: '11px',
                  fontWeight: 'bold',
                  textTransform: 'uppercase',
                  textAlign: 'center',
                  color: getRiskColor(regionalData.regional_prediction.risk_level_48h)
                }}
              >
                {regionalData.regional_prediction.risk_level_48h} Risk
              </div>
            </div>
          </div>

          {/* Comparison with Global */}
          <div
            style={{
              background: 'rgba(20, 30, 50, 0.5)',
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '20px'
            }}
          >
            <h4 style={{ fontSize: '14px', marginBottom: '12px', fontWeight: '600' }}>
              Regional vs Global Comparison
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '12px' }}>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>Global 24h:</div>
                <div style={{ fontWeight: 'bold' }}>{regionalData.global_comparison.global_probability_24h}%</div>
              </div>
              <div>
                <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>Difference:</div>
                <div style={{ fontWeight: 'bold', color: regionalData.global_comparison.difference_24h > 0 ? '#f87171' : '#4ade80' }}>
                  {regionalData.global_comparison.difference_24h > 0 ? '+' : ''}
                  {regionalData.global_comparison.difference_24h}%
                </div>
              </div>
            </div>
            <div style={{ marginTop: '12px', fontSize: '11px', color: 'rgba(255,255,255,0.6)' }}>
              Adjustment factor: {regionalData.regional_prediction.adjustment_factor}x
            </div>
          </div>

          {/* Regional TEC */}
          {regionalData.regional_tec && (
            <div
              style={{
                background: 'rgba(20, 30, 50, 0.5)',
                borderRadius: '12px',
                padding: '16px',
                marginBottom: '20px'
              }}
            >
              <h4 style={{ fontSize: '14px', marginBottom: '12px', fontWeight: '600' }}>
                Regional TEC (Total Electron Content)
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', fontSize: '12px' }}>
                <div>
                  <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>Mean:</div>
                  <div style={{ fontWeight: 'bold' }}>{regionalData.regional_tec.mean} TECU</div>
                </div>
                <div>
                  <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>Std Dev:</div>
                  <div style={{ fontWeight: 'bold' }}>{regionalData.regional_tec.std} TECU</div>
                </div>
                <div>
                  <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>Max:</div>
                  <div style={{ fontWeight: 'bold' }}>{regionalData.regional_tec.max} TECU</div>
                </div>
                <div>
                  <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: '4px' }}>Min:</div>
                  <div style={{ fontWeight: 'bold' }}>{regionalData.regional_tec.min} TECU</div>
                </div>
              </div>
            </div>
          )}

          {/* Explanation */}
          <div
            style={{
              padding: '14px',
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '8px',
              fontSize: '12px',
              color: 'rgba(255,255,255,0.7)',
              lineHeight: '1.6'
            }}
          >
            <div style={{ fontWeight: '600', marginBottom: '6px', color: '#60a5fa' }}>
              ℹ️ Why Regional Predictions Differ
            </div>
            <p style={{ margin: 0 }}>{regionalData.explanation}</p>
          </div>
        </>
      )}

      {/* Info Box */}
      <div
        style={{
          marginTop: '20px',
          padding: '14px',
          background: 'rgba(59, 130, 246, 0.1)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          borderRadius: '8px',
          fontSize: '12px',
          color: 'rgba(255,255,255,0.7)',
          lineHeight: '1.6'
        }}
      >
        <div style={{ fontWeight: '600', marginBottom: '6px', color: '#60a5fa' }}>
          About Regional Predictions
        </div>
        <ul style={{ margin: '0', paddingLeft: '20px' }}>
          <li><strong>High latitudes (60-75°):</strong> Enhanced storm risk in auroral zones</li>
          <li><strong>Mid latitudes (40-60°):</strong> Typical geomagnetic effects</li>
          <li><strong>Low latitudes (&lt;40°):</strong> Reduced storm impacts</li>
          <li><strong>Equatorial (&lt;20°):</strong> Minimal direct effects, but higher TEC</li>
        </ul>
      </div>
    </div>
  );
};

export default RegionalPrediction;
