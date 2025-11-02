/**
 * Ensemble Model Comparison Component
 * Shows V2.1, Climatology, and Ensemble forecasts side-by-side
 */
import React, { useState, useEffect } from 'react';
import api from '../services/api';

const EnsembleComparison = () => {
  const [ensembleData, setEnsembleData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [climatologyWeight, setClimatologyWeight] = useState(0.7);
  const [modelWeight, setModelWeight] = useState(0.3);

  useEffect(() => {
    fetchEnsembleData();
  }, [climatologyWeight, modelWeight]);

  const fetchEnsembleData = async () => {
    try {
      setLoading(true);
      const data = await api.getEnsemblePrediction(climatologyWeight, modelWeight);
      setEnsembleData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching ensemble data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleWeightChange = (climWeight) => {
    const clim = parseFloat(climWeight);
    setClimatologyWeight(clim);
    setModelWeight(1.0 - clim);
  };

  if (loading) {
    return (
      <div style={{
        background: 'rgba(0, 20, 40, 0.6)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(74, 144, 226, 0.3)',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '16px', color: 'rgba(255,255,255,0.7)' }}>
          Loading ensemble model...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        background: 'rgba(255, 107, 107, 0.1)',
        border: '2px solid #ff6b6b',
        borderRadius: '12px',
        padding: '24px'
      }}>
        <h3 style={{ color: '#ff6b6b', marginBottom: '8px' }}>Error Loading Ensemble</h3>
        <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px' }}>{error}</p>
      </div>
    );
  }

  if (!ensembleData) {
    return null;
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return '#4ade80';
      case 'moderate': return '#facc15';
      case 'elevated': return '#fb923c';
      case 'high': return '#f87171';
      case 'severe': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const riskLevel = ensembleData.risk_level_24h || ensembleData.risk_level || 'low';
  const stormProb = ensembleData.storm_probability_24h || 0;

  // Extract forecast arrays
  const climatologyForecast = ensembleData.climatology_forecast || [];
  const v2Forecast = ensembleData.v2_forecast || [];
  const ensembleForecast = ensembleData.tec_forecast_24h || [];

  // Calculate statistics
  const calcStats = (arr) => {
    if (!arr || arr.length === 0) return { mean: 0, min: 0, max: 0 };
    return {
      mean: (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(1),
      min: Math.min(...arr).toFixed(1),
      max: Math.max(...arr).toFixed(1)
    };
  };

  const climStats = calcStats(climatologyForecast);
  const v2Stats = calcStats(v2Forecast);
  const ensembleStats = calcStats(ensembleForecast);

  return (
    <div style={{
      background: 'rgba(0, 20, 40, 0.6)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(74, 144, 226, 0.3)',
    }}>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Ensemble Model Comparison</h2>
          <div style={{
            padding: '8px 16px',
            borderRadius: '20px',
            background: `${getRiskColor(riskLevel)}20`,
            border: `2px solid ${getRiskColor(riskLevel)}`,
            fontSize: '14px',
            fontWeight: '600',
            color: getRiskColor(riskLevel),
            textTransform: 'uppercase'
          }}>
            {riskLevel} Risk
          </div>
        </div>
        <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', marginBottom: '16px' }}>
          The main dashboard uses ensemble predictions (70/30 default). Adjust weights here to explore different combinations.
        </p>

        {/* Weight Slider */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '12px',
          padding: '16px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '14px', fontWeight: '600' }}>Model Weighting</span>
            <span style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)' }}>
              Climatology: {(climatologyWeight * 100).toFixed(0)}% | V2.1: {(modelWeight * 100).toFixed(0)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={climatologyWeight}
            onChange={(e) => handleWeightChange(e.target.value)}
            style={{
              width: '100%',
              height: '8px',
              borderRadius: '4px',
              background: `linear-gradient(to right, #4a90e2 0%, #4a90e2 ${climatologyWeight * 100}%, rgba(255,255,255,0.2) ${climatologyWeight * 100}%, rgba(255,255,255,0.2) 100%)`,
              outline: 'none',
              cursor: 'pointer'
            }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
            <span>Pure V2.1</span>
            <span style={{ fontWeight: '600', color: '#4a90e2' }}>Recommended (70/30)</span>
            <span>Pure Climatology</span>
          </div>
        </div>
      </div>

      {/* Comparison Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '20px'
      }}>
        {/* Climatology */}
        <ModelCard
          title="Climatology Baseline"
          subtitle="Historical Averaging"
          color="#9333ea"
          stats={climStats}
          description="Simple but reliable"
        />

        {/* V2.1 Neural Network */}
        <ModelCard
          title="V2.1 Neural Network"
          subtitle="BiLSTM-Attention"
          color="#f59e0b"
          stats={v2Stats}
          description="Storm detection focus"
        />

        {/* Ensemble */}
        <ModelCard
          title="Ensemble Forecast"
          subtitle={`${(climatologyWeight * 100).toFixed(0)}% Clim + ${(modelWeight * 100).toFixed(0)}% V2.1`}
          color="#10b981"
          stats={ensembleStats}
          description="Best of both methods"
          isEnsemble={true}
        />
      </div>

      {/* Storm Probability */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '12px',
        padding: '20px',
        border: '1px solid rgba(74, 144, 226, 0.2)'
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#4a90e2' }}>
          24-Hour Forecast Summary
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
          <StatItem label="Storm Probability" value={`${Math.round(stormProb * 100)}%`} color={getRiskColor(riskLevel)} />
          <StatItem label="Forecast Method" value={ensembleData.ensemble_method || 'Ensemble (70/30)'} color="#4a90e2" />
          <StatItem label="Mean TEC" value={`${ensembleStats.mean} TECU`} color="#10b981" />
          <StatItem label="TEC Range" value={`${ensembleStats.min}-${ensembleStats.max} TECU`} color="#6b7280" />
        </div>
      </div>

      {/* Validation Info */}
      <div style={{
        marginTop: '16px',
        padding: '12px',
        background: 'rgba(74, 144, 226, 0.1)',
        border: '1px solid rgba(74, 144, 226, 0.3)',
        borderRadius: '8px',
        fontSize: '13px',
        color: 'rgba(255,255,255,0.7)'
      }}>
        <strong>Validation:</strong> Ensemble model combines climatology (16.18 TECU RMSE) with V2.1 neural network (15.49 TECU RMSE, 4.3% improvement).
        Ensemble provides reliable baseline with improved storm detection.
      </div>
    </div>
  );
};

// Helper Components
const ModelCard = ({ title, subtitle, color, stats, description, isEnsemble = false }) => (
  <div style={{
    background: isEnsemble ? 'rgba(16, 185, 129, 0.1)' : 'rgba(0, 0, 0, 0.3)',
    borderRadius: '12px',
    padding: '16px',
    border: `2px solid ${color}${isEnsemble ? '' : '40'}`,
    boxShadow: isEnsemble ? `0 0 20px ${color}40` : 'none'
  }}>
    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
      {title}
    </div>
    <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)', marginBottom: '12px' }}>
      {subtitle}
    </div>
    <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '4px' }}>
      <span style={{ fontSize: '28px', fontWeight: 'bold', color }}>{stats.mean}</span>
      <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', marginLeft: '6px' }}>TECU</span>
    </div>
    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '8px' }}>
      Range: {stats.min} - {stats.max} TECU
    </div>
    <div style={{ fontSize: '11px', color: color, fontWeight: '600' }}>
      {description}
    </div>
  </div>
);

const StatItem = ({ label, value, color }) => (
  <div>
    <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
      {label}
    </div>
    <div style={{ fontSize: '16px', fontWeight: '600', color }}>
      {value}
    </div>
  </div>
);

export default EnsembleComparison;
