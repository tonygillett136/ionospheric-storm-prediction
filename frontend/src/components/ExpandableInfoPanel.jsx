/**
 * ExpandableInfoPanel Component
 * Educational content that can be expanded/collapsed
 */
import React, { useState } from 'react';

const ExpandableInfoPanel = ({ title, children, defaultExpanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div style={{
      background: 'rgba(74, 144, 226, 0.05)',
      border: '1px solid rgba(74, 144, 226, 0.2)',
      borderRadius: '12px',
      marginTop: '16px',
      overflow: 'hidden',
      transition: 'all 0.3s ease'
    }}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          width: '100%',
          padding: '14px 18px',
          background: 'transparent',
          border: 'none',
          color: '#fff',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '14px',
          fontWeight: '600',
          transition: 'background 0.2s'
        }}
        onMouseOver={(e) => e.currentTarget.style.background = 'rgba(74, 144, 226, 0.1)'}
        onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '16px' }}>📚</span>
          <span>{title}</span>
        </div>
        <span style={{
          fontSize: '18px',
          transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.3s'
        }}>
          ▼
        </span>
      </button>

      <div style={{
        maxHeight: isExpanded ? '2000px' : '0',
        opacity: isExpanded ? 1 : 0,
        transition: 'all 0.3s ease',
        overflow: 'hidden'
      }}>
        <div style={{
          padding: '16px 18px',
          fontSize: '13px',
          lineHeight: '1.7',
          color: 'rgba(255, 255, 255, 0.85)',
          borderTop: '1px solid rgba(74, 144, 226, 0.2)'
        }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default ExpandableInfoPanel;
