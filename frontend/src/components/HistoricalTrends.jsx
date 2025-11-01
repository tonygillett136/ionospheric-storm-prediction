/**
 * Historical Storm Trends Component
 * Shows storm probability history over multiple time periods
 */
import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../services/api';

const HistoricalTrends = () => {
  const [period, setPeriod] = useState('24h'); // 24h, week, month, year, 10year
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistoricalData(period);
  }, [period]);

  const fetchHistoricalData = async (timePeriod) => {
    setLoading(true);
    setError(null);

    try {
      // Map period to hours
      const hoursMap = {
        '24h': 24,
        'week': 168,
        'month': 720,
        'year': 8760,
        '10year': 87600
      };

      const hours = hoursMap[timePeriod];
      const response = await api.getTrends(hours);

      // Format data for charts
      const formattedData = formatDataForPeriod(response.data, timePeriod);
      setData(formattedData);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching historical data:', err);
      setError(err.message);
      setData(null);
      setLoading(false);
    }
  };

  const formatDataForPeriod = (rawData, timePeriod) => {
    if (!rawData || rawData.length === 0) {
      return null;
    }

    // Format based on period
    return rawData.map((item, idx) => ({
      timestamp: item.timestamp,
      stormProbability: item.stormProbability || 0, // Already 0-100 from API
      kpIndex: item.kp_index || 0,
      tecMean: item.tec_mean || 0,
      solarWind: item.solar_wind_speed || 0,
      index: idx
    }));
  };

  const generateSyntheticData = (timePeriod) => {
    const now = new Date();
    const dataPoints = {
      '24h': 24,
      'week': 168,
      'month': 180,
      'year': 365,
      '10year': 3650
    };

    const points = dataPoints[timePeriod];
    const interval = {
      '24h': 3600000, // 1 hour in ms
      'week': 3600000, // 1 hour
      'month': 14400000, // 4 hours
      'year': 86400000, // 1 day
      '10year': 86400000 // 1 day
    };

    const data = [];
    for (let i = points - 1; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - (i * interval[timePeriod]));
      const baseProb = 20 + Math.sin(i / 10) * 15 + Math.random() * 10;
      const kp = 2 + Math.sin(i / 5) * 2 + Math.random() * 1.5;

      data.push({
        timestamp: timestamp.toISOString(),
        stormProbability: Math.max(0, Math.min(100, baseProb)),
        kpIndex: Math.max(0, Math.min(9, kp)),
        tecMean: 20 + Math.sin(i / 8) * 10 + Math.random() * 5,
        solarWind: 350 + Math.sin(i / 12) * 100 + Math.random() * 50,
        index: points - i - 1
      });
    }

    return data;
  };

  const formatXAxis = (timestamp) => {
    const date = new Date(timestamp);

    switch (period) {
      case '24h':
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      case 'week':
        return date.toLocaleDateString('en-US', { weekday: 'short', hour: '2-digit' });
      case 'month':
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      case 'year':
        return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
      default:
        return date.toLocaleTimeString();
    }
  };

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    const date = new Date(payload[0].payload.timestamp);

    return (
      <div style={{
        background: 'rgba(0, 20, 40, 0.95)',
        border: '1px solid rgba(74, 144, 226, 0.5)',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '12px'
      }}>
        <div style={{ marginBottom: '8px', fontWeight: 'bold', color: '#4a90e2' }}>
          {date.toLocaleString()}
        </div>
        {payload.map((entry, index) => (
          <div key={index} style={{ color: entry.color, marginTop: '4px' }}>
            <strong>{entry.name}:</strong> {entry.value.toFixed(1)}{entry.name.includes('Probability') ? '%' : ''}
          </div>
        ))}
      </div>
    );
  };

  const getStormCount = () => {
    if (!data) return { total: 0, high: 0, moderate: 0 };

    const highThreshold = 60;
    const moderateThreshold = 40;

    const high = data.filter(d => d.stormProbability >= highThreshold).length;
    const moderate = data.filter(d => d.stormProbability >= moderateThreshold && d.stormProbability < highThreshold).length;

    return { total: data.length, high, moderate };
  };

  const stats = getStormCount();
  const avgProbability = data ? (data.reduce((sum, d) => sum + d.stormProbability, 0) / data.length).toFixed(1) : 0;
  const maxProbability = data ? Math.max(...data.map(d => d.stormProbability)).toFixed(1) : 0;

  return (
    <div style={{
      background: 'rgba(0, 20, 40, 0.6)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(74, 144, 226, 0.3)',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '20px', margin: 0 }}>Historical Storm Activity</h2>

        {/* Period Selector */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {['24h', 'week', 'month', 'year', '10year'].map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              style={{
                padding: '8px 16px',
                background: period === p ? '#4a90e2' : 'rgba(74, 144, 226, 0.2)',
                border: `1px solid ${period === p ? '#4a90e2' : 'rgba(74, 144, 226, 0.4)'}`,
                borderRadius: '8px',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: period === p ? 'bold' : 'normal',
                transition: 'all 0.2s'
              }}
            >
              {p === '24h' ? '24 Hours' :
               p === '10year' ? '10 Years' :
               p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Statistics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px', marginBottom: '20px' }}>
        <div style={{
          background: 'rgba(74, 144, 226, 0.1)',
          borderRadius: '8px',
          padding: '12px',
          border: '1px solid rgba(74, 144, 226, 0.3)'
        }}>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.6)', marginBottom: '4px' }}>Average Probability</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4a90e2' }}>{avgProbability}%</div>
        </div>

        <div style={{
          background: 'rgba(248, 113, 113, 0.1)',
          borderRadius: '8px',
          padding: '12px',
          border: '1px solid rgba(248, 113, 113, 0.3)'
        }}>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.6)', marginBottom: '4px' }}>Peak Probability</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f87171' }}>{maxProbability}%</div>
        </div>

        <div style={{
          background: 'rgba(251, 146, 60, 0.1)',
          borderRadius: '8px',
          padding: '12px',
          border: '1px solid rgba(251, 146, 60, 0.3)'
        }}>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.6)', marginBottom: '4px' }}>High Risk Periods</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fb923c' }}>{stats.high}</div>
        </div>

        <div style={{
          background: 'rgba(250, 204, 21, 0.1)',
          borderRadius: '8px',
          padding: '12px',
          border: '1px solid rgba(250, 204, 21, 0.3)'
        }}>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.6)', marginBottom: '4px' }}>Moderate Risk Periods</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#facc15' }}>{stats.moderate}</div>
        </div>
      </div>

      {/* Charts */}
      {loading ? (
        <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div>Loading historical data...</div>
        </div>
      ) : error ? (
        <div style={{ height: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '12px' }}>
          <div style={{ color: '#ff6b6b', fontSize: '16px', fontWeight: 'bold' }}>
            ⚠️ Unable to load historical data
          </div>
          <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: '14px', textAlign: 'center', maxWidth: '500px' }}>
            Historical data is currently unavailable. The system needs real observational data from sources like NASA CDDIS, NOAA SWPC, and GFZ Potsdam.
          </div>
          <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '12px', marginTop: '8px' }}>
            Note: Synthetic data display has been disabled to ensure data integrity
          </div>
        </div>
      ) : null}

      {data && (
        <>
          {/* Storm Probability Chart */}
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ fontSize: '14px', marginBottom: '12px', color: 'rgba(255,255,255,0.8)' }}>
              Storm Probability Trend
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f87171" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f87171" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatXAxis}
                  stroke="rgba(255,255,255,0.5)"
                  fontSize={10}
                />
                <YAxis
                  stroke="rgba(255,255,255,0.5)"
                  fontSize={10}
                  domain={[0, 100]}
                  label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft', style: { fill: 'rgba(255,255,255,0.5)', fontSize: 10 } }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                  type="monotone"
                  dataKey="stormProbability"
                  stroke="#f87171"
                  fillOpacity={1}
                  fill="url(#colorProb)"
                  name="Storm Probability"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Kp Index and TEC Chart */}
          <div>
            <h3 style={{ fontSize: '14px', marginBottom: '12px', color: 'rgba(255,255,255,0.8)' }}>
              Kp Index & TEC Trends
            </h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatXAxis}
                  stroke="rgba(255,255,255,0.5)"
                  fontSize={10}
                />
                <YAxis
                  yAxisId="left"
                  stroke="rgba(255,255,255,0.5)"
                  fontSize={10}
                  domain={[0, 9]}
                  label={{ value: 'Kp Index', angle: -90, position: 'insideLeft', style: { fill: 'rgba(255,255,255,0.5)', fontSize: 10 } }}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  stroke="rgba(255,255,255,0.5)"
                  fontSize={10}
                  label={{ value: 'TEC (TECU)', angle: 90, position: 'insideRight', style: { fill: 'rgba(255,255,255,0.5)', fontSize: 10 } }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="kpIndex"
                  stroke="#facc15"
                  strokeWidth={2}
                  dot={false}
                  name="Kp Index"
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="tecMean"
                  stroke="#4a90e2"
                  strokeWidth={2}
                  dot={false}
                  name="TEC Mean"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
};

export default HistoricalTrends;
