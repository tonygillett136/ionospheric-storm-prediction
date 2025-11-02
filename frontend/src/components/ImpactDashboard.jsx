/**
 * Impact Assessment Dashboard
 * Translates ionospheric storm predictions into actionable impacts
 */
import React, { useState, useEffect } from 'react';

const ImpactDashboard = () => {
  const [impacts, setImpacts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [latitude, setLatitude] = useState(45.0);

  useEffect(() => {
    fetchImpacts(latitude);
  }, [latitude]);

  const fetchImpacts = async (lat) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/v1/impact-assessment?latitude=${lat}`);
      const data = await response.json();
      setImpacts(data);
    } catch (error) {
      console.error('Error fetching impact assessment:', error);
    } finally {
      setLoading(false);
    }
  };

  const getImpactColor = (level) => {
    switch (level) {
      case 'minimal':
        return '#4ade80';
      case 'low':
        return '#86efac';
      case 'moderate':
        return '#facc15';
      case 'high':
        return '#fb923c';
      case 'severe':
        return '#f87171';
      default:
        return '#6b7280';
    }
  };

  const getSeverityColor = (score) => {
    if (score < 2) return '#4ade80';
    if (score < 4) return '#86efac';
    if (score < 6) return '#facc15';
    if (score < 8) return '#fb923c';
    return '#f87171';
  };

  const ImpactCard = ({ title, icon, data, children }) => {
    const color = getImpactColor(data.impact_level);
    const score = data.impact_score || 0;
    const percentage = (score / 10) * 100;

    return (
      <div
        style={{
          background: 'rgba(0, 20, 40, 0.4)',
          borderRadius: '12px',
          padding: '20px',
          border: `2px solid ${color}40`,
          flex: '1 1 300px',
          minWidth: '280px'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
          <div style={{ fontSize: '24px', marginRight: '10px' }}>{icon}</div>
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', margin: '0 0 4px 0' }}>
              {title}
            </h4>
            <div
              style={{
                fontSize: '11px',
                textTransform: 'uppercase',
                fontWeight: 'bold',
                color: color,
                letterSpacing: '0.5px'
              }}
            >
              {data.impact_level} Impact
            </div>
          </div>
        </div>

        {/* Impact score bar */}
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>Impact Score</span>
            <span style={{ fontSize: '14px', fontWeight: 'bold', color: color }}>
              {score.toFixed(1)}/10
            </span>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.1)', borderRadius: '10px', height: '10px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${percentage}%`,
                background: `linear-gradient(90deg, ${color}80, ${color})`,
                borderRadius: '10px',
                transition: 'width 0.5s ease'
              }}
            />
          </div>
        </div>

        {/* Description */}
        <div
          style={{
            fontSize: '13px',
            color: 'rgba(255,255,255,0.8)',
            marginBottom: '16px',
            lineHeight: '1.5'
          }}
        >
          {data.description}
        </div>

        {/* Custom content */}
        {children}

        {/* Recommendations */}
        {data.recommendations && data.recommendations.length > 0 && (
          <div
            style={{
              marginTop: '16px',
              padding: '12px',
              background: 'rgba(59, 130, 246, 0.1)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '8px'
            }}
          >
            <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#60a5fa', marginBottom: '8px' }}>
              RECOMMENDATIONS
            </div>
            <ul style={{ margin: '0', paddingLeft: '18px', fontSize: '12px', lineHeight: '1.6' }}>
              {data.recommendations.map((rec, idx) => (
                <li key={idx} style={{ marginBottom: '4px', color: 'rgba(255,255,255,0.7)' }}>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255,255,255,0.6)' }}>
        Loading impact assessment...
      </div>
    );
  }

  if (!impacts) {
    return (
      <div style={{ textAlign: 'center', padding: '40px', color: 'rgba(255,255,255,0.6)' }}>
        No impact data available
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
          Real-World Impact Assessment
        </h3>
        <p style={{ fontSize: '13px', color: 'rgba(255,255,255,0.6)', lineHeight: '1.5' }}>
          Translation of storm predictions into operational impacts for GPS, communications, satellites, and power infrastructure.
        </p>
      </div>

      {/* Overall severity */}
      {impacts.overall && (
        <div
          style={{
            background: 'rgba(20, 30, 50, 0.5)',
            borderRadius: '12px',
            padding: '20px',
            marginBottom: '20px',
            border: `2px solid ${getSeverityColor(impacts.overall.severity_score)}40`
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', marginBottom: '6px' }}>
                Overall Storm Severity
              </div>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: getSeverityColor(impacts.overall.severity_score) }}>
                {impacts.overall.severity_score}/10
              </div>
              <div
                style={{
                  fontSize: '12px',
                  textTransform: 'uppercase',
                  fontWeight: 'bold',
                  color: getSeverityColor(impacts.overall.severity_score),
                  letterSpacing: '0.8px',
                  marginTop: '4px'
                }}
              >
                {impacts.overall.severity_level} Severity
              </div>
            </div>
            {impacts.metadata && (
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
                <div style={{ marginBottom: '4px' }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>24h Probability:</span>{' '}
                  <span style={{ fontWeight: 'bold', color: '#60a5fa' }}>{impacts.metadata.probability_24h}%</span>
                </div>
                <div style={{ marginBottom: '4px' }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>Kp Index:</span>{' '}
                  <span style={{ fontWeight: 'bold' }}>{impacts.metadata.kp_index}</span>
                </div>
                <div>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>TEC Mean:</span>{' '}
                  <span style={{ fontWeight: 'bold' }}>{impacts.metadata.tec_mean.toFixed(1)} TECU</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Location selector */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)', marginRight: '10px' }}>
          Latitude (for regional effects):
        </label>
        <select
          value={latitude}
          onChange={(e) => setLatitude(parseFloat(e.target.value))}
          style={{
            padding: '6px 12px',
            borderRadius: '6px',
            background: 'rgba(0, 20, 40, 0.6)',
            border: '1px solid rgba(74, 144, 226, 0.3)',
            color: '#fff',
            fontSize: '13px'
          }}
        >
          <option value="0">Equator (0°)</option>
          <option value="30">Low Latitude (30°)</option>
          <option value="45">Mid Latitude (45°)</option>
          <option value="60">High Latitude (60°)</option>
          <option value="75">Polar (75°)</option>
        </select>
      </div>

      {/* Impact cards */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px', marginBottom: '20px' }}>
        {/* GPS Impact */}
        {impacts.gps && (
          <ImpactCard title="GPS Navigation" icon="🛰️" data={impacts.gps}>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>Normal Accuracy:</span>
                <span style={{ fontWeight: 'bold', color: '#4ade80' }}>{impacts.gps.normal_accuracy_m}m</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>Degraded Accuracy:</span>
                <span style={{ fontWeight: 'bold', color: '#f87171' }}>{impacts.gps.degraded_accuracy_m}m</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Accuracy Loss:</span>
                <span style={{ fontWeight: 'bold', color: '#fb923c' }}>{impacts.gps.accuracy_loss_pct}%</span>
              </div>
            </div>
          </ImpactCard>
        )}

        {/* Radio Impact */}
        {impacts.radio && (
          <ImpactCard title="HF Radio Communications" icon="📡" data={impacts.radio}>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '12px' }}>
              <div style={{ marginBottom: '8px' }}>
                <span style={{ color: 'rgba(255,255,255,0.5)' }}>Blackout Probability: </span>
                <span style={{ fontWeight: 'bold', color: '#f87171' }}>
                  {impacts.radio.blackout_probability_pct}%
                </span>
              </div>
              {impacts.radio.frequency_impacts && (
                <div style={{ fontSize: '11px' }}>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px', color: 'rgba(255,255,255,0.5)' }}>
                    Frequency Band Status:
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <span>3-10 MHz:</span>
                    <span style={{ textTransform: 'uppercase', fontSize: '10px', fontWeight: 'bold' }}>
                      {impacts.radio.frequency_impacts.low_band_3_10_mhz.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <span>10-20 MHz:</span>
                    <span style={{ textTransform: 'uppercase', fontSize: '10px', fontWeight: 'bold' }}>
                      {impacts.radio.frequency_impacts.mid_band_10_20_mhz.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>20-30 MHz:</span>
                    <span style={{ textTransform: 'uppercase', fontSize: '10px', fontWeight: 'bold' }}>
                      {impacts.radio.frequency_impacts.high_band_20_30_mhz.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </ImpactCard>
        )}

        {/* Satellite Impact */}
        {impacts.satellite && (
          <ImpactCard title="Satellite Operations" icon="🛸" data={impacts.satellite}>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>Atmospheric Drag:</span>
                <span style={{ fontWeight: 'bold', color: '#fb923c' }}>
                  {impacts.satellite.atmospheric_drag_multiplier}x
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>Charging Risk:</span>
                <span style={{ fontWeight: 'bold', color: '#f87171' }}>
                  {impacts.satellite.surface_charging_risk_pct}%
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>SEU Risk:</span>
                <span style={{ fontWeight: 'bold', color: '#facc15' }}>
                  {impacts.satellite.single_event_upset_risk_pct}%
                </span>
              </div>
            </div>
          </ImpactCard>
        )}

        {/* Power Grid Impact */}
        {impacts.power_grid && (
          <ImpactCard title="Power Grid" icon="⚡" data={impacts.power_grid}>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span>GIC Risk:</span>
                <span style={{ fontWeight: 'bold', color: '#fb923c' }}>
                  {impacts.power_grid.gic_risk_pct}%
                </span>
              </div>
              <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.5)', marginTop: '8px' }}>
                {impacts.power_grid.affected_regions}
              </div>
            </div>
          </ImpactCard>
        )}
      </div>

      {/* Information box */}
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
          ℹ️ About Impact Assessment
        </div>
        <ul style={{ margin: '0', paddingLeft: '20px' }}>
          <li><strong>GPS:</strong> Based on Klobuchar ionospheric model - accuracy degrades with TEC and Kp index</li>
          <li><strong>HF Radio:</strong> ITU propagation standards - lower frequencies more affected by absorption</li>
          <li><strong>Satellites:</strong> Drag increases with storm intensity, charging/SEU risks scale with Kp</li>
          <li><strong>Power Grid:</strong> GIC (Geomagnetically Induced Currents) primarily affect high-latitude regions (&gt;60°)</li>
        </ul>
      </div>
    </div>
  );
};

export default ImpactDashboard;
