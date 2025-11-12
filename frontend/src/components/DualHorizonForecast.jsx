/**
 * Dual-Horizon Storm Forecast Component
 * Displays 24h and 48h storm predictions with confidence levels
 */
import React from 'react';

const DualHorizonForecast = ({ prediction }) => {
  if (!prediction || !prediction.horizons) {
    return <div>Loading...</div>;
  }

  const { horizons } = prediction;

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

  const HorizonCard = ({ horizon, data, label, isHighConfidence }) => {
    const color = getRiskColor(data.risk_level);
    const probability = data.probability / 100;
    const rotation = probability * 180;

    return (
      <div
        style={{
          flex: 1,
          background: 'rgba(0, 20, 40, 0.4)',
          borderRadius: '12px',
          padding: '20px',
          border: `2px ${isHighConfidence ? 'solid' : 'dashed'} ${isHighConfidence ? 'rgba(74, 144, 226, 0.4)' : 'rgba(251, 146, 60, 0.4)'}`,
          position: 'relative',
          minWidth: '280px'
        }}
      >
        {/* Confidence badge */}
        <div
          style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            background: isHighConfidence ? 'rgba(34, 197, 94, 0.2)' : 'rgba(251, 146, 60, 0.2)',
            border: `1px solid ${isHighConfidence ? 'rgba(34, 197, 94, 0.4)' : 'rgba(251, 146, 60, 0.4)'}`,
            borderRadius: '6px',
            padding: '4px 10px',
            fontSize: '10px',
            fontWeight: 'bold',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            color: isHighConfidence ? '#4ade80' : '#fb923c'
          }}
        >
          {data.confidence_label} confidence
        </div>

        <h4 style={{ marginBottom: '12px', fontSize: '14px', fontWeight: '600', color: 'rgba(255,255,255,0.8)' }}>
          {label}
        </h4>

        {/* Mini gauge */}
        <div style={{ position: 'relative', width: '180px', height: '100px', margin: '0 auto 10px' }}>
          <svg width="180" height="100" style={{ overflow: 'visible' }}>
            {/* Background arc */}
            <path
              d="M 20 80 A 70 70 0 0 1 160 80"
              fill="none"
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="14"
              strokeLinecap="round"
            />

            {/* Colored arc */}
            <path
              d="M 20 80 A 70 70 0 0 1 160 80"
              fill="none"
              stroke={color}
              strokeWidth="14"
              strokeLinecap="round"
              strokeDasharray={`${probability * 220} 220`}
              style={{ transition: 'stroke-dasharray 0.5s ease' }}
            />

            {/* Needle */}
            <line
              x1="90"
              y1="80"
              x2="90"
              y2="25"
              stroke={color}
              strokeWidth="2.5"
              strokeLinecap="round"
              style={{
                transformOrigin: '90px 80px',
                transform: `rotate(${rotation - 90}deg)`,
                transition: 'transform 0.5s ease',
              }}
            />

            {/* Center dot */}
            <circle cx="90" cy="80" r="6" fill={color} />
          </svg>

          {/* Percentage */}
          <div
            style={{
              position: 'absolute',
              bottom: '-20px',
              left: '50%',
              transform: 'translateX(-50%)',
              fontSize: '32px',
              fontWeight: 'bold',
              color: color,
            }}
          >
            {Math.round(data.probability)}%
          </div>
        </div>

        {/* Risk level */}
        <div
          style={{
            marginTop: '20px',
            padding: '8px 16px',
            borderRadius: '6px',
            background: `${color}15`,
            border: `1.5px solid ${color}`,
            fontWeight: '600',
            fontSize: '13px',
            textTransform: 'uppercase',
            letterSpacing: '0.8px',
            color: color,
            textAlign: 'center'
          }}
        >
          {data.risk_level} Risk
        </div>

        {/* Confidence meter */}
        <div style={{ marginTop: '16px', textAlign: 'center' }}>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', marginBottom: '6px' }}>
            Prediction Confidence
          </div>
          <div style={{ background: 'rgba(255,255,255,0.1)', borderRadius: '10px', height: '8px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${data.confidence}%`,
                background: isHighConfidence ? 'linear-gradient(90deg, #22c55e, #4ade80)' : 'linear-gradient(90deg, #f59e0b, #fb923c)',
                borderRadius: '10px',
                transition: 'width 0.5s ease'
              }}
            />
          </div>
          <div style={{ fontSize: '12px', color: isHighConfidence ? '#4ade80' : '#fb923c', marginTop: '4px', fontWeight: '600' }}>
            {Math.round(data.confidence)}%
          </div>
        </div>

        {/* Scale markers */}
        <div
          style={{
            marginTop: '16px',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '10px',
            color: 'rgba(255, 255, 255, 0.4)',
            paddingLeft: '20px',
            paddingRight: '20px',
          }}
        >
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>
    );
  };

  return (
    <div
      style={{
        background: 'rgba(0, 20, 40, 0.6)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(74, 144, 226, 0.3)',
      }}
    >
      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
          Multi-Horizon Storm Forecast
        </h3>
        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.5' }}>
          Extended forecasts provide early warning but have reduced accuracy.
          48-hour predictions show approximately 10% lower accuracy than 24-hour forecasts.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
        <HorizonCard
          horizon="24h"
          data={horizons['24h']}
          label="24-Hour Forecast"
          isHighConfidence={true}
        />
        <HorizonCard
          horizon="48h"
          data={horizons['48h']}
          label="48-Hour Forecast"
          isHighConfidence={false}
        />
      </div>

      {/* Information box */}
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
          ℹ️ About Extended Forecasts
        </div>
        <ul style={{ margin: '0', paddingLeft: '20px' }}>
          <li><strong>24-hour predictions:</strong> High accuracy (60.6%), tested and reliable for operational decisions</li>
          <li><strong>48-hour predictions:</strong> Medium accuracy (54.4%), useful for early warning and planning</li>
          <li><strong>Confidence levels:</strong> Indicate reliability based on empirical backtesting on real historical data</li>
        </ul>
      </div>
    </div>
  );
};

export default DualHorizonForecast;
