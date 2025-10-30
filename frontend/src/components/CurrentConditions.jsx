/**
 * Current Conditions Panel
 * Comprehensive real-time ionospheric and space weather state
 */
import React from 'react';

// Helper functions defined outside component
const calculateMean = (values) => {
  if (!values || values.length === 0) return 0;
  const flat = values.flat();
  return (flat.reduce((a, b) => a + b, 0) / flat.length).toFixed(1);
};

const calculateMax = (values) => {
  if (!values || values.length === 0) return 0;
  return Math.max(...values.flat()).toFixed(1);
};

const calculateMin = (values) => {
  if (!values || values.length === 0) return 0;
  return Math.min(...values.flat()).toFixed(1);
};

const getConditionLevel = (value, thresholds) => {
  if (value === null || value === undefined) return 'unknown';
  if (value < thresholds.low) return 'low';
  if (value < thresholds.moderate) return 'moderate';
  if (value < thresholds.high) return 'high';
  return 'severe';
};

const getConditionColor = (level) => {
  switch (level) {
    case 'low': return '#4ade80';
    case 'moderate': return '#facc15';
    case 'high': return '#fb923c';
    case 'severe': return '#f87171';
    default: return '#6b7280';
  }
};

const CurrentConditions = ({ tecData, spaceWeather, prediction }) => {
  // Calculate TEC statistics
  const tecStats = tecData ? {
    mean: calculateMean(tecData.tec_values),
    max: calculateMax(tecData.tec_values),
    min: calculateMin(tecData.tec_values),
  } : null;

  // Determine geomagnetic activity level
  const kpLevel = getConditionLevel(spaceWeather?.kp_index, {
    low: 3, moderate: 5, high: 7
  });

  // Determine solar wind level
  const swLevel = getConditionLevel(spaceWeather?.solar_wind?.speed, {
    low: 400, moderate: 500, high: 600
  });

  // Determine IMF Bz level (negative is more concerning)
  const bzValue = spaceWeather?.imf_bz || 0;
  const bzLevel = bzValue < -10 ? 'severe' : bzValue < -5 ? 'high' : bzValue < 0 ? 'moderate' : 'low';

  return (
    <div style={{
      background: 'rgba(0, 20, 40, 0.6)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(74, 144, 226, 0.3)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Current Ionospheric Conditions</h2>
        <div style={{
          padding: '8px 16px',
          borderRadius: '20px',
          background: `${getConditionColor(prediction?.risk_level || 'unknown')}20`,
          border: `2px solid ${getConditionColor(prediction?.risk_level || 'unknown')}`,
          fontSize: '14px',
          fontWeight: '600',
          color: getConditionColor(prediction?.risk_level || 'unknown'),
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {prediction?.risk_level || 'Unknown'} Activity
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '24px'
      }}>
        {/* TEC Overview */}
        <MetricCard
          title="Total Electron Content"
          value={tecStats?.mean || '--'}
          unit="TECU"
          subtitle="Global Average"
          color="#4a90e2"
          details={[
            { label: 'Min', value: `${tecStats?.min || '--'} TECU` },
            { label: 'Max', value: `${tecStats?.max || '--'} TECU` }
          ]}
        />

        {/* Geomagnetic Activity */}
        <MetricCard
          title="Geomagnetic Activity"
          value={spaceWeather?.kp_index?.toFixed(1) || '--'}
          unit="Kp"
          subtitle={kpLevel === 'low' ? 'Quiet' : kpLevel === 'moderate' ? 'Unsettled' : 'Active'}
          color={getConditionColor(kpLevel)}
          details={[
            { label: 'Status', value: kpLevel.toUpperCase() }
          ]}
        />

        {/* Solar Wind */}
        <MetricCard
          title="Solar Wind"
          value={spaceWeather?.solar_wind?.speed?.toFixed(0) || '--'}
          unit="km/s"
          subtitle={swLevel === 'low' ? 'Normal' : 'Elevated'}
          color={getConditionColor(swLevel)}
          details={[
            { label: 'Density', value: `${spaceWeather?.solar_wind?.density?.toFixed(1) || '--'} p/cm³` }
          ]}
        />

        {/* IMF Bz */}
        <MetricCard
          title="IMF Bz Component"
          value={Math.abs(bzValue).toFixed(1)}
          unit="nT"
          subtitle={bzValue < 0 ? 'Southward' : 'Northward'}
          color={getConditionColor(bzLevel)}
          details={[
            { label: 'Direction', value: bzValue < 0 ? '↓ South (Unstable)' : '↑ North (Stable)' }
          ]}
        />
      </div>

      {/* Detailed Analysis */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '12px',
        padding: '20px',
        border: '1px solid rgba(74, 144, 226, 0.2)'
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px', color: '#4a90e2' }}>
          Detailed Analysis
        </h3>

        <div style={{ display: 'grid', gap: '12px' }}>
          {/* Solar Activity */}
          <DetailRow
            icon="☀️"
            title="Solar Activity"
            value={`F10.7: ${spaceWeather?.f107_flux?.toFixed(0) || '--'} sfu`}
            description={getSolarActivityDesc(spaceWeather?.f107_flux)}
            level={spaceWeather?.f107_flux > 150 ? 'high' : spaceWeather?.f107_flux > 100 ? 'moderate' : 'low'}
          />

          {/* Geomagnetic Conditions */}
          <DetailRow
            icon="🧲"
            title="Geomagnetic Field"
            value={`Kp ${spaceWeather?.kp_index?.toFixed(1) || '--'}`}
            description={getGeomagneticDesc(spaceWeather?.kp_index)}
            level={kpLevel}
          />

          {/* Ionospheric State */}
          <DetailRow
            icon="🌐"
            title="Ionospheric State"
            value={`TEC ${tecStats?.mean || '--'} TECU average`}
            description={getTECDesc(parseFloat(tecStats?.mean))}
            level={getTECLevel(parseFloat(tecStats?.mean))}
          />

          {/* Storm Risk */}
          <DetailRow
            icon="⚡"
            title="Storm Risk (24h)"
            value={`${prediction?.storm_probability_24h ? Math.round(prediction.storm_probability_24h * 100) : '--'}% probability`}
            description={getStormRiskDesc(prediction?.storm_probability_24h)}
            level={prediction?.risk_level || 'unknown'}
          />

          {/* Space Weather Environment */}
          <DetailRow
            icon="🛰️"
            title="Space Environment"
            value={getOverallCondition(kpLevel, swLevel, bzLevel)}
            description="Combined assessment of all parameters"
            level={getWorstLevel([kpLevel, swLevel, bzLevel])}
          />
        </div>
      </div>

      {/* Recommendations */}
      {(prediction?.risk_level === 'high' || prediction?.risk_level === 'severe') && (
        <div style={{
          marginTop: '16px',
          padding: '16px',
          background: 'rgba(251, 146, 60, 0.1)',
          border: '2px solid #fb923c',
          borderRadius: '8px'
        }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '24px' }}>⚠️</span>
            <div>
              <h4 style={{ color: '#fb923c', fontWeight: '600', marginBottom: '8px' }}>
                Elevated Storm Risk
              </h4>
              <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>
                <li>GPS/GNSS accuracy may be degraded</li>
                <li>HF radio communications may be affected</li>
                <li>Satellite operations should monitor closely</li>
                <li>Aurora may be visible at lower latitudes</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper Components
const MetricCard = ({ title, value, unit, subtitle, color, details }) => (
  <div style={{
    background: 'rgba(0, 0, 0, 0.3)',
    borderRadius: '12px',
    padding: '16px',
    border: `1px solid ${color}40`
  }}>
    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
      {title}
    </div>
    <div style={{ display: 'flex', alignItems: 'baseline', marginBottom: '4px' }}>
      <span style={{ fontSize: '32px', fontWeight: 'bold', color }}>{value}</span>
      {unit && <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.5)', marginLeft: '6px' }}>{unit}</span>}
    </div>
    <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)', marginBottom: '12px' }}>
      {subtitle}
    </div>
    {details && details.map((detail, idx) => (
      <div key={idx} style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginTop: '4px' }}>
        <span style={{ color: 'rgba(255,255,255,0.4)' }}>{detail.label}:</span> {detail.value}
      </div>
    ))}
  </div>
);

const DetailRow = ({ icon, title, value, description, level }) => {
  const colors = {
    low: '#4ade80',
    moderate: '#facc15',
    high: '#fb923c',
    severe: '#f87171',
    unknown: '#6b7280'
  };

  return (
    <div style={{
      display: 'flex',
      gap: '12px',
      padding: '12px',
      background: 'rgba(0, 0, 0, 0.2)',
      borderRadius: '8px',
      borderLeft: `3px solid ${colors[level]}`
    }}>
      <span style={{ fontSize: '20px' }}>{icon}</span>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <span style={{ fontWeight: '600', fontSize: '14px' }}>{title}</span>
          <span style={{ fontSize: '13px', color: colors[level], fontWeight: '600' }}>{value}</span>
        </div>
        <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
          {description}
        </div>
      </div>
    </div>
  );
};

// Helper Functions
const getSolarActivityDesc = (f107) => {
  if (!f107) return 'No data available';
  if (f107 < 80) return 'Very low solar activity';
  if (f107 < 120) return 'Low to moderate solar activity';
  if (f107 < 180) return 'Moderate to high solar activity';
  return 'High solar activity';
};

const getGeomagneticDesc = (kp) => {
  if (!kp) return 'No data available';
  if (kp < 3) return 'Quiet geomagnetic conditions';
  if (kp < 5) return 'Unsettled geomagnetic conditions';
  if (kp < 7) return 'Active to minor storm conditions';
  if (kp < 8) return 'Major storm conditions';
  return 'Severe storm conditions';
};

const getTECDesc = (tec) => {
  if (!tec) return 'No data available';
  if (tec < 10) return 'Very low ionization levels';
  if (tec < 20) return 'Low ionization levels';
  if (tec < 35) return 'Normal ionization levels';
  if (tec < 50) return 'Elevated ionization levels';
  return 'High ionization levels';
};

const getTECLevel = (tec) => {
  if (!tec) return 'unknown';
  if (tec < 20) return 'low';
  if (tec < 35) return 'moderate';
  if (tec < 50) return 'high';
  return 'severe';
};

const getStormRiskDesc = (prob) => {
  if (!prob) return 'Unable to assess';
  const p = prob * 100;
  if (p < 20) return 'Low probability of ionospheric disturbances';
  if (p < 40) return 'Moderate probability of minor disturbances';
  if (p < 60) return 'Elevated probability of ionospheric storms';
  if (p < 80) return 'High probability of significant storms';
  return 'Very high probability of severe storms';
};

const getOverallCondition = (kp, sw, bz) => {
  const worst = getWorstLevel([kp, sw, bz]);
  if (worst === 'severe') return 'Severe conditions';
  if (worst === 'high') return 'Active conditions';
  if (worst === 'moderate') return 'Unsettled conditions';
  return 'Quiet conditions';
};

const getWorstLevel = (levels) => {
  const priority = { severe: 4, high: 3, moderate: 2, low: 1, unknown: 0 };
  return levels.reduce((worst, current) =>
    priority[current] > priority[worst] ? current : worst
  , 'unknown');
};

export default CurrentConditions;
