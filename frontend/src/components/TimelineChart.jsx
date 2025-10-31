/**
 * Timeline Chart Component
 * Displays hourly storm probabilities for the next 24 hours
 */
import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const TimelineChart = ({ hourlyProbabilities = [], tecForecast = [] }) => {
  // Prepare data for the chart
  const data = hourlyProbabilities.map((prob, index) => ({
    hour: `+${index + 1}h`,
    probability: (prob * 100).toFixed(1),
    tec: tecForecast[index] ? tecForecast[index].toFixed(1) : null,
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            background: 'rgba(0, 20, 40, 0.95)',
            padding: '12px',
            borderRadius: '8px',
            border: '1px solid rgba(74, 144, 226, 0.5)',
          }}
        >
          <p style={{ margin: 0, fontWeight: 'bold', marginBottom: '8px' }}>{label}</p>
          {payload.map((entry, index) => (
            <p
              key={index}
              style={{
                margin: 0,
                color: entry.color,
                fontSize: '13px',
              }}
            >
              {entry.name}: {entry.value}
              {entry.name === 'Storm Probability' ? '%' : ' TECU'}
            </p>
          ))}
        </div>
      );
    }
    return null;
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
      <h3 style={{ marginBottom: '20px', fontSize: '18px', fontWeight: '600' }}>
        24-Hour Forecast Timeline
      </h3>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorProb" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#f87171" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#f87171" stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="colorTEC" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4ade80" stopOpacity={0.6} />
              <stop offset="95%" stopColor="#4ade80" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
          <XAxis
            dataKey="hour"
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            yAxisId="left"
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
            label={{
              value: 'Probability (%)',
              angle: -90,
              position: 'insideLeft',
              style: { fill: 'rgba(255, 255, 255, 0.7)' },
            }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="rgba(255, 255, 255, 0.5)"
            style={{ fontSize: '12px' }}
            label={{
              value: 'TEC (TECU)',
              angle: 90,
              position: 'insideRight',
              style: { fill: 'rgba(255, 255, 255, 0.7)' },
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ paddingTop: '10px' }}
            iconType="line"
          />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="probability"
            stroke="#f87171"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorProb)"
            name="Storm Probability"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="tec"
            stroke="#4ade80"
            strokeWidth={2}
            dot={{ fill: '#4ade80', r: 3 }}
            name="TEC Forecast"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TimelineChart;
