/**
 * InfoTooltip Component
 * Provides expandable educational content without cluttering the UI
 */
import React, { useState } from 'react';

const InfoTooltip = ({ title, content, position = 'top' }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div style={{ position: 'relative', display: 'inline-block', marginLeft: '8px' }}>
      <button
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '18px',
          height: '18px',
          borderRadius: '50%',
          border: '1.5px solid rgba(74, 144, 226, 0.6)',
          background: 'rgba(74, 144, 226, 0.2)',
          color: '#4a90e2',
          fontSize: '11px',
          fontWeight: 'bold',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.2s',
          padding: 0,
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.background = 'rgba(74, 144, 226, 0.4)';
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.background = 'rgba(74, 144, 226, 0.2)';
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        ?
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          zIndex: 1000,
          width: '320px',
          background: 'rgba(10, 14, 39, 0.98)',
          border: '1px solid rgba(74, 144, 226, 0.5)',
          borderRadius: '12px',
          padding: '16px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          ...(position === 'top' ? { bottom: '28px', left: '50%', transform: 'translateX(-50%)' } : {}),
          ...(position === 'bottom' ? { top: '28px', left: '50%', transform: 'translateX(-50%)' } : {}),
          ...(position === 'left' ? { right: '28px', top: '50%', transform: 'translateY(-50%)' } : {}),
          ...(position === 'right' ? { left: '28px', top: '50%', transform: 'translateY(-50%)' } : {}),
        }}>
          <div style={{
            fontSize: '13px',
            fontWeight: '600',
            color: '#4a90e2',
            marginBottom: '8px',
            borderBottom: '1px solid rgba(74, 144, 226, 0.3)',
            paddingBottom: '6px'
          }}>
            {title}
          </div>
          <div style={{
            fontSize: '12px',
            lineHeight: '1.6',
            color: 'rgba(255, 255, 255, 0.9)'
          }}>
            {content}
          </div>
        </div>
      )}
    </div>
  );
};

export default InfoTooltip;
