/**
 * Parameter Card Component
 * Displays a single space weather parameter with trend indicator
 */
import React from 'react';
import InfoTooltip from './InfoTooltip';

const ParameterCard = ({ title, value, unit, trend, status, description, infoContent }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'normal':
        return '#4ade80';
      case 'elevated':
        return '#facc15';
      case 'warning':
        return '#fb923c';
      case 'critical':
        return '#f87171';
      default:
        return '#6b7280';
    }
  };

  const getTrendIcon = (trend) => {
    if (trend > 0.1) return '↑';
    if (trend < -0.1) return '↓';
    return '→';
  };

  const statusColor = getStatusColor(status);

  return (
    <div
      style={{
        background: 'rgba(0, 20, 40, 0.6)',
        borderRadius: '12px',
        padding: '20px',
        border: `1px solid ${statusColor}40`,
        transition: 'all 0.3s ease',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '12px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <h4
            style={{
              fontSize: '14px',
              fontWeight: '500',
              color: 'rgba(255, 255, 255, 0.7)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            {title}
          </h4>
          {infoContent && (
            <InfoTooltip
              title={infoContent.title}
              content={infoContent.content}
              position="bottom"
            />
          )}
        </div>
        <div
          style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: statusColor,
            boxShadow: `0 0 10px ${statusColor}`,
          }}
        />
      </div>

      {/* Value */}
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          marginBottom: '8px',
        }}
      >
        <span
          style={{
            fontSize: '32px',
            fontWeight: 'bold',
            color: '#ffffff',
            marginRight: '8px',
          }}
        >
          {value !== null && value !== undefined ? value : '--'}
        </span>
        {unit && (
          <span
            style={{
              fontSize: '16px',
              color: 'rgba(255, 255, 255, 0.5)',
            }}
          >
            {unit}
          </span>
        )}
      </div>

      {/* Trend and Description */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        {description && (
          <span
            style={{
              fontSize: '12px',
              color: 'rgba(255, 255, 255, 0.6)',
            }}
          >
            {description}
          </span>
        )}
        {trend !== undefined && (
          <span
            style={{
              fontSize: '18px',
              color: trend > 0 ? '#f87171' : trend < 0 ? '#4ade80' : '#6b7280',
              fontWeight: 'bold',
            }}
          >
            {getTrendIcon(trend)}
          </span>
        )}
      </div>
    </div>
  );
};

export default ParameterCard;
