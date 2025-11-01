import React, { useState } from 'react';
import {
  BarChart, Bar, LineChart, Line, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Area, AreaChart, Cell
} from 'recharts';
import api from '../services/api';

const BacktestWorkshop = () => {
  // Set default dates to a known working range (30 days ago to yesterday)
  const getDefaultDates = () => {
    const end = new Date();
    end.setDate(end.getDate() - 1); // Yesterday
    const start = new Date();
    start.setDate(start.getDate() - 30); // 30 days ago
    return {
      start: start.toISOString().split('T')[0],
      end: end.toISOString().split('T')[0]
    };
  };

  const defaults = getDefaultDates();
  const [startDate, setStartDate] = useState(defaults.start);
  const [endDate, setEndDate] = useState(defaults.end);
  const [stormThreshold, setStormThreshold] = useState(40.0);
  const [sampleInterval, setSampleInterval] = useState(24); // Daily by default
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Threshold optimization state
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResults, setOptimizationResults] = useState(null);
  const [optimizationMethod, setOptimizationMethod] = useState('f1'); // 'f1', 'youden', 'cost'
  const [showOptimizationChart, setShowOptimizationChart] = useState(false);

  // Quick preset date ranges
  const applyPreset = (preset) => {
    const end = new Date();
    const start = new Date();

    switch (preset) {
      case 'week':
        start.setDate(end.getDate() - 7);
        break;
      case 'month':
        start.setMonth(end.getMonth() - 1);
        break;
      case '3months':
        start.setMonth(end.getMonth() - 3);
        break;
      case '6months':
        start.setMonth(end.getMonth() - 6);
        break;
      case 'year':
        start.setFullYear(end.getFullYear() - 1);
        break;
      default:
        return;
    }

    setStartDate(start.toISOString().split('T')[0]);
    setEndDate(end.toISOString().split('T')[0]);
  };

  const runBacktest = async () => {
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const data = await api.post('/backtest/run', {
        start_date: startDate + 'T00:00:00',  // Add time component
        end_date: endDate + 'T00:00:00',
        storm_threshold: stormThreshold,
        sample_interval_hours: sampleInterval
      });

      setResults(data);
      setActiveTab('overview');
    } catch (err) {
      console.error('Backtest error:', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to run backtest';
      setError(detail);
    } finally {
      setIsLoading(false);
    }
  };

  const optimizeThreshold = async () => {
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    setIsOptimizing(true);
    setError(null);
    setOptimizationResults(null);

    try {
      const data = await api.post('/backtest/optimize-threshold', {
        start_date: startDate + 'T00:00:00',
        end_date: endDate + 'T00:00:00',
        optimization_method: optimizationMethod,
        cost_false_alarm: 1.0,
        cost_missed_storm: 5.0,
        sample_interval_hours: sampleInterval
      });

      setOptimizationResults(data);
      setStormThreshold(data.optimization.optimal_threshold);
      setShowOptimizationChart(true);
    } catch (err) {
      console.error('Optimization error:', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to optimize threshold';
      setError(detail);
    } finally {
      setIsOptimizing(false);
    }
  };

  const exportResults = (format) => {
    if (!results) return;

    if (format === 'json') {
      const dataStr = JSON.stringify(results, null, 2);
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
      const exportFileDefaultName = `backtest_${startDate}_to_${endDate}.json`;

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    } else if (format === 'csv') {
      const predictions = results.predictions;
      const headers = Object.keys(predictions[0]).join(',');
      const rows = predictions.map(p => Object.values(p).join(','));
      const csv = [headers, ...rows].join('\n');

      const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
      const exportFileDefaultName = `backtest_predictions_${startDate}_to_${endDate}.csv`;

      const linkElement = document.createElement('a');
      linkElement.setAttribute('href', dataUri);
      linkElement.setAttribute('download', exportFileDefaultName);
      linkElement.click();
    }
  };

  const renderMetricCard = (title, value, subtitle, color = '#3b82f6') => (
    <div style={{
      background: 'white',
      borderRadius: '8px',
      padding: '20px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      border: '1px solid #e5e7eb'
    }}>
      <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
        {title}
      </div>
      <div style={{ fontSize: '32px', fontWeight: 'bold', color: color, marginBottom: '4px' }}>
        {value}
      </div>
      {subtitle && (
        <div style={{ fontSize: '12px', color: '#9ca3af' }}>
          {subtitle}
        </div>
      )}
    </div>
  );

  const renderOverview = () => {
    const { metrics, metadata, summary } = results;

    return (
      <div>
        {/* Key Metrics Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px',
          marginBottom: '24px'
        }}>
          {renderMetricCard(
            'Accuracy',
            `${(metrics.accuracy * 100).toFixed(1)}%`,
            'Overall classification accuracy',
            metrics.accuracy >= 0.8 ? '#10b981' : metrics.accuracy >= 0.6 ? '#f59e0b' : '#ef4444'
          )}
          {renderMetricCard(
            'Precision',
            `${(metrics.precision * 100).toFixed(1)}%`,
            'Correct storm predictions',
            '#8b5cf6'
          )}
          {renderMetricCard(
            'Recall (Hit Rate)',
            `${(metrics.recall * 100).toFixed(1)}%`,
            'Storms successfully detected',
            '#ec4899'
          )}
          {renderMetricCard(
            'F1 Score',
            metrics.f1_score.toFixed(3),
            'Harmonic mean of precision & recall',
            '#06b6d4'
          )}
          {renderMetricCard(
            'RMSE',
            summary.average_absolute_error.toFixed(2),
            'Average prediction error (%)',
            '#f97316'
          )}
          {renderMetricCard(
            'False Alarm Rate',
            `${(metrics.false_alarm_rate * 100).toFixed(1)}%`,
            'FP / (FP + TN) - False alarms among non-storm predictions',
            '#ef4444'
          )}
        </div>

        {/* Confusion Matrix */}
        <div style={{
          background: 'white',
          borderRadius: '8px',
          padding: '24px',
          marginBottom: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
            Confusion Matrix
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', maxWidth: '500px' }}>
            <div style={{ background: '#dcfce7', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#166534' }}>
                {metrics.true_positives}
              </div>
              <div style={{ fontSize: '14px', color: '#15803d', marginTop: '4px' }}>
                True Positives
              </div>
              <div style={{ fontSize: '12px', color: '#16a34a', marginTop: '2px' }}>
                Correctly predicted storms
              </div>
            </div>
            <div style={{ background: '#fee2e2', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#991b1b' }}>
                {metrics.false_positives}
              </div>
              <div style={{ fontSize: '14px', color: '#dc2626', marginTop: '4px' }}>
                False Positives
              </div>
              <div style={{ fontSize: '12px', color: '#ef4444', marginTop: '2px' }}>
                False alarms
              </div>
            </div>
            <div style={{ background: '#fef3c7', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#92400e' }}>
                {metrics.false_negatives}
              </div>
              <div style={{ fontSize: '14px', color: '#b45309', marginTop: '4px' }}>
                False Negatives
              </div>
              <div style={{ fontSize: '12px', color: '#d97706', marginTop: '2px' }}>
                Missed storms
              </div>
            </div>
            <div style={{ background: '#dbeafe', padding: '20px', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '28px', fontWeight: 'bold', color: '#1e3a8a' }}>
                {metrics.true_negatives}
              </div>
              <div style={{ fontSize: '14px', color: '#1e40af', marginTop: '4px' }}>
                True Negatives
              </div>
              <div style={{ fontSize: '12px', color: '#2563eb', marginTop: '2px' }}>
                Correctly predicted non-storms
              </div>
            </div>
          </div>

          {/* Add explanatory note when FAR is extreme */}
          {(metrics.false_alarm_rate === 1.0 || metrics.false_alarm_rate === 0.0) && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: '#fef3c7',
              borderRadius: '6px',
              fontSize: '13px',
              color: '#92400e',
              border: '1px solid #fbbf24'
            }}>
              <strong>💡 Note:</strong> {metrics.false_alarm_rate === 1.0
                ? `FAR is 100% because all predictions exceeded the ${metadata.storm_threshold}% threshold when no actual storms occurred (TN=0). Try increasing the threshold to see different results.`
                : `FAR is 0% because no predictions exceeded the ${metadata.storm_threshold}% threshold. All non-storms were correctly identified. Try lowering the threshold to see different results.`
              }
            </div>
          )}
        </div>

        {/* Summary Stats */}
        <div style={{
          background: 'white',
          borderRadius: '8px',
          padding: '24px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
            Test Summary
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', fontSize: '14px' }}>
            <div><strong>Duration:</strong> {metadata.duration_days} days</div>
            <div><strong>Total Predictions:</strong> {metadata.total_predictions}</div>
            <div><strong>Actual Storms:</strong> {metrics.total_storms_actual}</div>
            <div><strong>Predicted Storms:</strong> {metrics.total_storms_predicted}</div>
            <div><strong>Storm Threshold:</strong> {metadata.storm_threshold}%</div>
            <div><strong>Sample Interval:</strong> {metadata.sample_interval_hours}h</div>
            <div><strong>R² Score:</strong> {metrics.r_squared.toFixed(4)}</div>
            <div><strong>MAE:</strong> {metrics.mae.toFixed(2)}%</div>
          </div>
        </div>
      </div>
    );
  };

  const renderPredictionsChart = () => {
    const predictions = results.predictions.slice(0, 500); // Limit for performance

    const chartData = predictions.map(p => ({
      timestamp: new Date(p.timestamp).toLocaleDateString(),
      predicted: p.predicted_probability,
      actual: p.actual_probability,
      threshold: results.metadata.storm_threshold
    }));

    return (
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
          Predictions vs Actual (First 500 samples)
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tick={{ fontSize: 12 }}
              interval={Math.floor(chartData.length / 10)}
            />
            <YAxis label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#3b82f6"
              strokeWidth={2}
              name="Predicted"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#10b981"
              strokeWidth={2}
              name="Actual"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="threshold"
              stroke="#ef4444"
              strokeWidth={1}
              strokeDasharray="5 5"
              name="Threshold"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderScatterPlot = () => {
    const scatterData = results.predictions.map(p => ({
      predicted: p.predicted_probability,
      actual: p.actual_probability
    }));

    return (
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
          Predicted vs Actual Scatter Plot
        </h3>
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="actual"
              name="Actual"
              label={{ value: 'Actual Probability (%)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              type="number"
              dataKey="predicted"
              name="Predicted"
              label={{ value: 'Predicted Probability (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter
              name="Predictions"
              data={scatterData}
              fill="#3b82f6"
              fillOpacity={0.6}
            />
          </ScatterChart>
        </ResponsiveContainer>
        <p style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px', textAlign: 'center' }}>
          Points near the diagonal line indicate accurate predictions
        </p>
      </div>
    );
  };

  const renderErrorDistribution = () => {
    // Create histogram bins for error distribution
    const errors = results.predictions.map(p => p.absolute_error);
    const binSize = 5;
    const maxError = Math.ceil(Math.max(...errors) / binSize) * binSize;
    const bins = [];

    for (let i = 0; i <= maxError; i += binSize) {
      const binErrors = errors.filter(e => e >= i && e < i + binSize);
      bins.push({
        range: `${i}-${i + binSize}`,
        count: binErrors.length
      });
    }

    return (
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
          Error Distribution
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={bins}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="range" label={{ value: 'Absolute Error (%)', position: 'insideBottom', offset: -5 }} />
            <YAxis label={{ value: 'Frequency', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Bar dataKey="count" fill="#8b5cf6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderDetailedResults = () => {
    return (
      <div>
        {renderPredictionsChart()}
        {renderScatterPlot()}
        {renderErrorDistribution()}
      </div>
    );
  };

  const renderEventsList = (events, title, emptyMessage, color) => {
    return (
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
          {title} ({events.length})
        </h3>
        {events.length === 0 ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '20px' }}>
            {emptyMessage}
          </p>
        ) : (
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table style={{ width: '100%', fontSize: '14px', borderCollapse: 'collapse' }}>
              <thead style={{ background: '#f9fafb', position: 'sticky', top: 0 }}>
                <tr>
                  <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Time</th>
                  <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Predicted</th>
                  <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Actual</th>
                  <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Error</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px' }}>
                      {new Date(event.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', color: color }}>
                      {event.predicted_probability.toFixed(1)}%
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right' }}>
                      {event.actual_probability.toFixed(1)}%
                    </td>
                    <td style={{ padding: '12px', textAlign: 'right', color: '#6b7280' }}>
                      {event.absolute_error.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  const renderAnalysis = () => {
    const { analysis } = results;

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {renderEventsList(
          analysis.missed_storms,
          'Missed Storms (False Negatives)',
          'No storms were missed! Perfect detection rate.',
          '#f59e0b'
        )}
        {renderEventsList(
          analysis.false_alarms,
          'False Alarms (False Positives)',
          'No false alarms! Perfect specificity.',
          '#ef4444'
        )}
        {renderEventsList(
          analysis.best_predictions.slice(0, 10),
          'Best Predictions (Lowest Error)',
          'No predictions available.',
          '#10b981'
        )}
        {renderEventsList(
          analysis.worst_predictions.slice(0, 10),
          'Worst Predictions (Highest Error)',
          'No predictions available.',
          '#ef4444'
        )}
      </div>
    );
  };

  const renderAllPredictions = () => {
    return (
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold' }}>
            All Predictions ({results.predictions.length})
          </h3>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => exportResults('csv')}
              style={{
                padding: '8px 16px',
                background: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Export CSV
            </button>
            <button
              onClick={() => exportResults('json')}
              style={{
                padding: '8px 16px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Export JSON
            </button>
          </div>
        </div>
        <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
          <table style={{ width: '100%', fontSize: '14px', borderCollapse: 'collapse' }}>
            <thead style={{ background: '#f9fafb', position: 'sticky', top: 0 }}>
              <tr>
                <th style={{ padding: '12px', textAlign: 'left', borderBottom: '2px solid #e5e7eb' }}>Timestamp</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Predicted</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Actual</th>
                <th style={{ padding: '12px', textAlign: 'right', borderBottom: '2px solid #e5e7eb' }}>Error</th>
                <th style={{ padding: '12px', textAlign: 'center', borderBottom: '2px solid #e5e7eb' }}>Classification</th>
              </tr>
            </thead>
            <tbody>
              {results.predictions.map((pred, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px' }}>
                    {new Date(pred.timestamp).toLocaleString()}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#3b82f6' }}>
                    {pred.predicted_probability.toFixed(1)}%
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#10b981' }}>
                    {pred.actual_probability.toFixed(1)}%
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', color: '#6b7280' }}>
                    {pred.absolute_error.toFixed(1)}%
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      background: pred.correct_classification ? '#dcfce7' : '#fee2e2',
                      color: pred.correct_classification ? '#166534' : '#991b1b'
                    }}>
                      {pred.correct_classification ? '✓ Correct' : '✗ Incorrect'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
        Backtesting Workshop
      </h1>
      <p style={{ color: '#6b7280', marginBottom: '24px', fontSize: '16px' }}>
        Validate model performance by testing predictions against historical data
      </p>

      {/* Configuration Panel */}
      <div style={{
        background: 'white',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e5e7eb'
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
          Configure Backtest
        </h2>

        {/* Quick Presets */}
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
            Quick Presets
          </label>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {['week', 'month', '3months', '6months', 'year'].map(preset => (
              <button
                key={preset}
                onClick={() => applyPreset(preset)}
                style={{
                  padding: '8px 16px',
                  background: '#f3f4f6',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                Last {preset === '3months' ? '3 Months' : preset === '6months' ? '6 Months' : preset.charAt(0).toUpperCase() + preset.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '20px' }}>
          {/* Start Date */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>

          {/* End Date */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            />
          </div>

          {/* Storm Threshold */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <label style={{ fontSize: '14px', fontWeight: '500' }}>
                Storm Threshold: {stormThreshold}%
                {optimizationResults && (
                  <span style={{ marginLeft: '8px', fontSize: '12px', color: '#10b981', fontWeight: 'normal' }}>
                    ⭐ Optimized
                  </span>
                )}
              </label>
              <button
                onClick={optimizeThreshold}
                disabled={isOptimizing || !startDate || !endDate}
                style={{
                  padding: '6px 12px',
                  background: isOptimizing ? '#6b7280' : '#10b981',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isOptimizing ? 'not-allowed' : 'pointer',
                  fontSize: '12px',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                {isOptimizing ? '⏳ Optimizing...' : '🎯 Auto-Optimize'}
              </button>
            </div>

            {/* Optimization Method Selector */}
            <div style={{ marginBottom: '8px' }}>
              <label style={{ color: '#888', fontSize: '12px', marginBottom: '6px', display: 'block' }}>Optimization Method:</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                {[
                  {
                    value: 'f1',
                    label: 'F1 Score',
                    description: 'Best balance between precision and recall. Recommended for general use.'
                  },
                  {
                    value: 'youden',
                    label: "Youden's J",
                    description: 'Maximizes True Positive Rate + True Negative Rate. Best for ROC optimization.'
                  },
                  {
                    value: 'cost',
                    label: 'Cost-Based',
                    description: 'Minimizes cost where missed storms are 5x more expensive than false alarms.'
                  }
                ].map(method => (
                  <label
                    key={method.value}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      cursor: 'pointer',
                      padding: '8px',
                      background: optimizationMethod === method.value ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255,255,255,0.02)',
                      borderRadius: '6px',
                      border: `1px solid ${optimizationMethod === method.value ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255,255,255,0.1)'}`
                    }}
                  >
                    <input
                      type="radio"
                      value={method.value}
                      checked={optimizationMethod === method.value}
                      onChange={(e) => setOptimizationMethod(e.target.value)}
                      style={{ marginTop: '2px' }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: '500', marginBottom: '2px' }}>{method.label}</div>
                      <div style={{ color: '#888', fontSize: '11px' }}>{method.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div style={{ fontSize: '12px', color: '#888', marginBottom: '8px' }}>
              Probability threshold to classify a prediction as a storm. Lower = more sensitive (more detections, possibly more false alarms).
            </div>
            <input
              type="range"
              min="10"
              max="90"
              step="5"
              value={stormThreshold}
              onChange={(e) => setStormThreshold(parseFloat(e.target.value))}
              style={{ width: '100%' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
              <span>10%</span>
              <span>90%</span>
            </div>
          </div>

          {/* Sample Interval */}
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
              Sample Interval
            </label>
            <select
              value={sampleInterval}
              onChange={(e) => setSampleInterval(parseInt(e.target.value))}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px'
              }}
            >
              <option value={1}>Every Hour</option>
              <option value={3}>Every 3 Hours</option>
              <option value={6}>Every 6 Hours</option>
              <option value={12}>Every 12 Hours</option>
              <option value={24}>Daily</option>
            </select>
          </div>
        </div>

        {/* Run Button */}
        <button
          onClick={runBacktest}
          disabled={isLoading || !startDate || !endDate}
          style={{
            width: '100%',
            padding: '12px',
            background: isLoading || !startDate || !endDate ? '#d1d5db' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: isLoading || !startDate || !endDate ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Running Backtest...' : 'Run Backtest'}
        </button>

        {error && (
          <div style={{
            marginTop: '16px',
            padding: '12px',
            background: '#fee2e2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            color: '#991b1b',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {/* Threshold Optimization Chart */}
        {showOptimizationChart && optimizationResults && (
          <div style={{
            marginTop: '20px',
            background: 'rgba(0, 20, 40, 0.6)',
            borderRadius: '16px',
            padding: '24px',
            border: '1px solid rgba(74, 144, 226, 0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '18px', margin: 0 }}>📊 Threshold Performance Analysis</h3>
              <button
                onClick={() => setShowOptimizationChart(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#888',
                  cursor: 'pointer',
                  fontSize: '20px'
                }}
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <div style={{ fontSize: '14px', marginBottom: '4px' }}>
                <strong>Optimal Threshold:</strong> {optimizationResults.optimization.optimal_threshold}%
              </div>
              <div style={{ fontSize: '12px', color: '#888' }}>
                Method: {optimizationMethod === 'f1' ? 'F1 Score' : optimizationMethod === 'youden' ? "Youden's J" : 'Cost-Based'} |
                Score: {optimizationResults.optimization.best_score.toFixed(3)}
              </div>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={optimizationResults.optimization.threshold_sweep}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                  dataKey="threshold"
                  stroke="rgba(255,255,255,0.5)"
                  label={{ value: 'Threshold (%)', position: 'insideBottom', offset: -5, style: { fill: 'rgba(255,255,255,0.7)' } }}
                />
                <YAxis
                  stroke="rgba(255,255,255,0.5)"
                  domain={[0, 1]}
                  label={{ value: 'Score', angle: -90, position: 'insideLeft', style: { fill: 'rgba(255,255,255,0.7)' } }}
                />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(0, 20, 40, 0.95)',
                    border: '1px solid rgba(74, 144, 226, 0.5)',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line type="monotone" dataKey="f1_score" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} name="F1 Score" />
                <Line type="monotone" dataKey="precision" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} name="Precision" />
                <Line type="monotone" dataKey="recall" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} name="Recall" />
                <Line
                  type="monotone"
                  dataKey="threshold"
                  stroke="transparent"
                  dot={(props) => {
                    const { cx, cy, payload } = props;
                    if (payload.threshold === optimizationResults.optimization.optimal_threshold) {
                      return (
                        <circle cx={cx} cy={cy} r={6} fill="#10b981" stroke="#fff" strokeWidth={2} />
                      );
                    }
                    return null;
                  }}
                  name="Optimal"
                />
              </LineChart>
            </ResponsiveContainer>

            <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', fontSize: '12px' }}>
              <div style={{ padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ color: '#888', marginBottom: '4px' }}>F1 Score</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#10b981' }}>
                  {optimizationResults.optimization.optimal_metrics.f1_score.toFixed(3)}
                </div>
              </div>
              <div style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ color: '#888', marginBottom: '4px' }}>Precision</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#3b82f6' }}>
                  {optimizationResults.optimization.optimal_metrics.precision.toFixed(3)}
                </div>
              </div>
              <div style={{ padding: '12px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px', textAlign: 'center' }}>
                <div style={{ color: '#888', marginBottom: '4px' }}>Recall</div>
                <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#f59e0b' }}>
                  {optimizationResults.optimization.optimal_metrics.recall.toFixed(3)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {results && (
        <div>
          {/* Tabs */}
          <div style={{
            display: 'flex',
            gap: '4px',
            marginBottom: '16px',
            borderBottom: '2px solid #e5e7eb'
          }}>
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'charts', label: 'Charts & Analysis' },
              { id: 'analysis', label: 'Detailed Analysis' },
              { id: 'all', label: 'All Predictions' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '12px 24px',
                  background: activeTab === tab.id ? 'white' : 'transparent',
                  border: 'none',
                  borderBottom: activeTab === tab.id ? '2px solid #3b82f6' : 'none',
                  color: activeTab === tab.id ? '#3b82f6' : '#6b7280',
                  fontSize: '14px',
                  fontWeight: activeTab === tab.id ? 'bold' : 'normal',
                  cursor: 'pointer',
                  marginBottom: '-2px'
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'charts' && renderDetailedResults()}
            {activeTab === 'analysis' && renderAnalysis()}
            {activeTab === 'all' && renderAllPredictions()}
          </div>
        </div>
      )}
    </div>
  );
};

export default BacktestWorkshop;
