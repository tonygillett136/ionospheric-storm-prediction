/**
 * Storm Probability Gauge Component
 * Displays the current storm probability with a visual gauge
 */
import React from 'react';

const StormGauge = ({ probability = 0, riskLevel = 'low' }) => {
  const percentage = Math.round(probability * 100);

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

  const color = getRiskColor(riskLevel);

  // Calculate gauge rotation (0-180 degrees)
  const rotation = probability * 180;

  return (
    <div
      style={{
        background: 'rgba(0, 20, 40, 0.6)',
        borderRadius: '16px',
        padding: '24px',
        border: '1px solid rgba(74, 144, 226, 0.3)',
        textAlign: 'center',
      }}
    >
      <h3 style={{ marginBottom: '20px', fontSize: '18px', fontWeight: '600' }}>
        Storm Probability (24h)
      </h3>

      <div style={{ position: 'relative', width: '220px', height: '120px', margin: '0 auto' }}>
        {/* Gauge background */}
        <svg width="220" height="120" style={{ overflow: 'visible' }}>
          {/* Background arc */}
          <path
            d="M 20 100 A 90 90 0 0 1 200 100"
            fill="none"
            stroke="rgba(255, 255, 255, 0.1)"
            strokeWidth="20"
            strokeLinecap="round"
          />

          {/* Colored arc */}
          <path
            d="M 20 100 A 90 90 0 0 1 200 100"
            fill="none"
            stroke={color}
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${probability * 283} 283`}
            style={{ transition: 'stroke-dasharray 0.5s ease' }}
          />

          {/* Needle */}
          <line
            x1="110"
            y1="100"
            x2="110"
            y2="30"
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
            style={{
              transformOrigin: '110px 100px',
              transform: `rotate(${rotation - 90}deg)`,
              transition: 'transform 0.5s ease',
            }}
          />

          {/* Center dot */}
          <circle cx="110" cy="100" r="8" fill={color} />
        </svg>

        {/* Percentage display */}
        <div
          style={{
            position: 'absolute',
            bottom: '-25px',
            left: '50%',
            transform: 'translateX(-50%)',
            fontSize: '36px',
            fontWeight: 'bold',
            color: color,
          }}
        >
          {percentage}%
        </div>
      </div>

      {/* Risk level indicator */}
      <div
        style={{
          marginTop: '30px',
          padding: '12px 24px',
          borderRadius: '8px',
          background: `${color}20`,
          border: `2px solid ${color}`,
          fontWeight: '600',
          fontSize: '16px',
          textTransform: 'uppercase',
          letterSpacing: '1px',
          color: color,
        }}
      >
        {riskLevel} Risk
      </div>

      {/* Scale markers */}
      <div
        style={{
          marginTop: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: 'rgba(255, 255, 255, 0.6)',
          paddingLeft: '10px',
          paddingRight: '10px',
        }}
      >
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>
    </div>
  );
};

export default StormGauge;
