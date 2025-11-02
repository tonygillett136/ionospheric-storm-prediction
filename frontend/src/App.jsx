/**
 * Main Application Component - Without 3D Globe
 * Ionospheric Storm Prediction System
 */
import React, { useState, useEffect } from 'react';
import StormGauge from './components/StormGauge';
import DualHorizonForecast from './components/DualHorizonForecast';
import ParameterCard from './components/ParameterCard';
import TimelineChart from './components/TimelineChart';
import CurrentConditions from './components/CurrentConditions';
import ExpandableInfoPanel from './components/ExpandableInfoPanel';
import HistoricalTrends from './components/HistoricalTrends';
import Glossary from './components/Glossary';
import Globe3D from './components/Globe3D';
import BacktestWorkshop from './components/BacktestWorkshop';
import ImpactDashboard from './components/ImpactDashboard';
import api from './services/api';
import { getEducationalContent } from './utils/educationalContent';

function App() {
  const [tecData, setTecData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [spaceWeather, setSpaceWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [activeView, setActiveView] = useState('dashboard');

  useEffect(() => {
    console.log('App mounted');
    fetchAllData();

    try {
      api.connectWebSocket(handleWebSocketMessage);
    } catch (err) {
      console.error('WebSocket error:', err);
    }

    const interval = setInterval(fetchAllData, 60000);
    return () => {
      clearInterval(interval);
      api.disconnectWebSocket();
    };
  }, []);

  const fetchAllData = async () => {
    try {
      console.log('Fetching data...');
      const [tecResponse, predictionResponse, weatherResponse] = await Promise.all([
        api.getCurrentTEC().catch(() => ({ tec_data: null })),
        api.getPrediction().catch(() => null),
        api.getCurrentSpaceWeather().catch(() => ({})),
      ]);

      console.log('Data fetched successfully');
      setTecData(tecResponse?.tec_data);
      setPrediction(predictionResponse);
      setSpaceWeather(weatherResponse);
      setLastUpdate(new Date());
      setLoading(false);
      setConnectionStatus('connected');
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (message) => {
    try {
      if (message.type === 'initial_data') {
        if (message.data) setTecData(message.data.tec_data);
        if (message.prediction) setPrediction(message.prediction);
      }
      setConnectionStatus('connected');
    } catch (err) {
      console.error('WS error:', err);
    }
  };

  const getKpStatus = (kp) => {
    if (!kp) return 'unknown';
    if (kp < 4) return 'normal';
    if (kp < 5) return 'elevated';
    return 'warning';
  };

  const getKpDescription = (kp) => {
    if (!kp) return 'No data';
    if (kp < 4) return 'Quiet';
    if (kp < 5) return 'Unsettled';
    return 'Storm';
  };

  console.log('Rendering App, loading:', loading, 'error:', error);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0e27, #1a1a2e, #16213e)',
        color: '#fff',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '4px solid rgba(74, 144, 226, 0.3)',
          borderTop: '4px solid #4a90e2',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}/>
        <p style={{ marginTop: '20px' }}>Loading ionospheric data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0e27, #1a1a2e, #16213e)',
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          background: 'rgba(255, 107, 107, 0.1)',
          border: '2px solid #ff6b6b',
          borderRadius: '12px',
          padding: '32px',
          maxWidth: '500px'
        }}>
          <h2 style={{ color: '#ff6b6b', marginBottom: '16px' }}>Error</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0e27, #1a1a2e, #16213e)',
      color: '#fff',
      padding: '20px'
    }}>
      <header style={{
        marginBottom: '30px',
        padding: '20px',
        background: 'rgba(0, 20, 40, 0.6)',
        borderRadius: '16px',
        border: '1px solid rgba(74, 144, 226, 0.3)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
          flexWrap: 'wrap',
          gap: '20px'
        }}>
          <div>
            <h1 style={{
              fontSize: '32px',
              marginBottom: '8px',
              background: 'linear-gradient(90deg, #4a90e2, #50e3c2)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Ionospheric Storm Prediction
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.7)' }}>Real-time monitoring and 24-hour forecasting</p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              background: connectionStatus === 'connected' ? '#4ade80' : '#f87171',
              boxShadow: '0 0 10px currentColor'
            }}/>
            <span>{connectionStatus === 'connected' ? 'Live' : 'Offline'}</span>
            {lastUpdate && (
              <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginLeft: '8px' }}>
                {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '8px',
          borderBottom: '1px solid rgba(74, 144, 226, 0.3)',
          paddingBottom: '0'
        }}>
          <button
            onClick={() => setActiveView('dashboard')}
            style={{
              padding: '12px 24px',
              background: activeView === 'dashboard' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
              border: 'none',
              borderBottom: activeView === 'dashboard' ? '3px solid #4a90e2' : '3px solid transparent',
              color: activeView === 'dashboard' ? '#4a90e2' : 'rgba(255,255,255,0.7)',
              fontSize: '14px',
              fontWeight: activeView === 'dashboard' ? 'bold' : 'normal',
              cursor: 'pointer',
              transition: 'all 0.2s',
              borderRadius: '8px 8px 0 0'
            }}
          >
            📊 Dashboard
          </button>
          <button
            onClick={() => setActiveView('backtest')}
            style={{
              padding: '12px 24px',
              background: activeView === 'backtest' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
              border: 'none',
              borderBottom: activeView === 'backtest' ? '3px solid #4a90e2' : '3px solid transparent',
              color: activeView === 'backtest' ? '#4a90e2' : 'rgba(255,255,255,0.7)',
              fontSize: '14px',
              fontWeight: activeView === 'backtest' ? 'bold' : 'normal',
              cursor: 'pointer',
              transition: 'all 0.2s',
              borderRadius: '8px 8px 0 0'
            }}
          >
            🔬 Backtest Workshop
          </button>
          <button
            onClick={() => setActiveView('impact')}
            style={{
              padding: '12px 24px',
              background: activeView === 'impact' ? 'rgba(74, 144, 226, 0.2)' : 'transparent',
              border: 'none',
              borderBottom: activeView === 'impact' ? '3px solid #4a90e2' : '3px solid transparent',
              color: activeView === 'impact' ? '#4a90e2' : 'rgba(255,255,255,0.7)',
              fontSize: '14px',
              fontWeight: activeView === 'impact' ? 'bold' : 'normal',
              cursor: 'pointer',
              transition: 'all 0.2s',
              borderRadius: '8px 8px 0 0'
            }}
          >
            🎯 Impact Assessment
          </button>
        </div>
      </header>

      <main style={{ maxWidth: '1600px', margin: '0 auto' }}>
        {/* Dashboard View */}
        {activeView === 'dashboard' && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '20px' }}>
              {/* 3D Globe Visualization */}
              <div style={{
                background: 'rgba(0, 20, 40, 0.6)',
                borderRadius: '16px',
                padding: '24px',
                border: '1px solid rgba(74, 144, 226, 0.3)'
              }}>
                <h2 style={{ marginBottom: '16px' }}>Global TEC Distribution</h2>
                <Globe3D tecData={tecData} />
              </div>

              {/* Storm Forecast */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <DualHorizonForecast prediction={prediction} />
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div style={{
                    background: 'rgba(0, 20, 40, 0.6)',
                    borderRadius: '12px',
                    padding: '16px',
                    border: '1px solid rgba(74, 144, 226, 0.3)',
                    textAlign: 'center'
                  }}>
                    <span style={{ display: 'block', fontSize: '12px', color: 'rgba(255,255,255,0.6)', marginBottom: '8px' }}>
                      Max Probability
                    </span>
                    <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: '#4a90e2' }}>
                      {prediction?.max_probability ? `${Math.round(prediction.max_probability * 100)}%` : '--'}
                    </span>
                  </div>
                  <div style={{
                    background: 'rgba(0, 20, 40, 0.6)',
                    borderRadius: '12px',
                    padding: '16px',
                    border: '1px solid rgba(74, 144, 226, 0.3)',
                    textAlign: 'center'
                  }}>
                    <span style={{ display: 'block', fontSize: '12px', color: 'rgba(255,255,255,0.6)', marginBottom: '8px' }}>
                      Avg Probability
                    </span>
                    <span style={{ display: 'block', fontSize: '24px', fontWeight: 'bold', color: '#4a90e2' }}>
                      {prediction?.average_probability ? `${Math.round(prediction.average_probability * 100)}%` : '--'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Current Conditions - Comprehensive State */}
            <CurrentConditions
              tecData={tecData}
              spaceWeather={spaceWeather}
              prediction={prediction}
            />

            {/* Parameters Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', margin: '20px 0' }}>
              <ParameterCard
                title="Kp Index"
                value={spaceWeather?.kp_index?.toFixed(1)}
                status={getKpStatus(spaceWeather?.kp_index)}
                description={getKpDescription(spaceWeather?.kp_index)}
                infoContent={getEducationalContent('kpIndex')}
              />
              <ParameterCard
                title="Solar Wind Speed"
                value={spaceWeather?.solar_wind?.speed?.toFixed(0)}
                unit="km/s"
                status={spaceWeather?.solar_wind?.speed > 500 ? 'warning' : 'normal'}
                description={spaceWeather?.solar_wind?.speed > 500 ? 'Elevated' : 'Normal'}
                infoContent={getEducationalContent('solarWind')}
              />
              <ParameterCard
                title="IMF Bz"
                value={spaceWeather?.imf_bz?.toFixed(1)}
                unit="nT"
                status={spaceWeather?.imf_bz < -5 ? 'warning' : 'normal'}
                description={spaceWeather?.imf_bz < 0 ? 'Southward' : 'Northward'}
                infoContent={getEducationalContent('imfBz')}
              />
              <ParameterCard
                title="F10.7 Flux"
                value={spaceWeather?.f107_flux?.toFixed(0)}
                unit="sfu"
                status={spaceWeather?.f107_flux > 150 ? 'elevated' : 'normal'}
                description="Solar activity"
                infoContent={getEducationalContent('f107')}
              />
            </div>

            {/* Timeline Chart */}
            {prediction && (
              <TimelineChart
                hourlyProbabilities={prediction.hourly_probabilities || []}
                tecForecast={prediction.tec_forecast_24h || []}
              />
            )}

            {/* Historical Trends */}
            <HistoricalTrends />

            {/* Glossary */}
            <Glossary />

            {/* Educational Content */}
            <ExpandableInfoPanel title="Learn About Ionospheric Storms">
              <div style={{ marginBottom: '16px' }}>
                <strong style={{ color: '#4a90e2' }}>What are Ionospheric Storms?</strong>
                <p style={{ marginTop: '8px' }}>
                  {getEducationalContent('ionosphericStorms').content.substring(0, 400)}...
                </p>
              </div>
              <div>
                <strong style={{ color: '#4a90e2' }}>Real-World Impacts:</strong>
                <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                  <li>GPS positioning errors (meters to tens of meters)</li>
                  <li>HF radio communication disruptions</li>
                  <li>Satellite navigation signal loss</li>
                  <li>Increased satellite drag</li>
                  <li>Aurora visible at lower latitudes</li>
                </ul>
              </div>
            </ExpandableInfoPanel>

            <ExpandableInfoPanel title="Understanding the Prediction Model">
              <div style={{ marginBottom: '16px' }}>
                <strong style={{ color: '#4a90e2' }}>How It Works:</strong>
                <p style={{ marginTop: '8px' }}>
                  This system uses a hybrid CNN-LSTM deep learning model that analyzes 8 different parameters
                  over the past 24 hours to predict storm probability for the next 24 hours. The model combines:
                </p>
                <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                  <li><strong>CNN layers</strong> - Extract spatial patterns from the data</li>
                  <li><strong>LSTM layers</strong> - Capture temporal dependencies and trends</li>
                  <li><strong>Multi-task learning</strong> - Predicts both storm probability and TEC values</li>
                </ul>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <strong style={{ color: '#4a90e2' }}>Input Parameters:</strong>
                <p style={{ marginTop: '8px', fontSize: '12px' }}>
                  TEC (mean & std) • Kp index • Solar wind speed • IMF Bz • F10.7 flux • Time of day • Season
                </p>
              </div>
              <div>
                <strong style={{ color: '#4a90e2' }}>Risk Levels:</strong>
                <ul style={{ marginTop: '8px', paddingLeft: '20px', fontSize: '12px' }}>
                  <li><span style={{ color: '#4ade80' }}>●</span> <strong>Low</strong>: &lt;20% probability - Normal operations</li>
                  <li><span style={{ color: '#facc15' }}>●</span> <strong>Moderate</strong>: 20-40% - Minor effects possible</li>
                  <li><span style={{ color: '#fb923c' }}>●</span> <strong>Elevated</strong>: 40-60% - Noticeable impacts likely</li>
                  <li><span style={{ color: '#f87171' }}>●</span> <strong>High/Severe</strong>: &gt;60% - Significant disruptions expected</li>
                </ul>
              </div>
            </ExpandableInfoPanel>

            <ExpandableInfoPanel title="Applications & Use Cases">
              <div style={{ marginBottom: '12px' }}>
                <strong style={{ color: '#4a90e2' }}>Who Uses This Information:</strong>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '12px' }}>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>✈️ Aviation</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>GPS navigation, polar routes, ADS-B systems</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>🛰️ Satellite Ops</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>Orbit determination, comm links, drag estimation</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>⚡ Power Grids</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>GIC warnings, transformer protection</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>🗺️ Surveying</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>High-precision GNSS, RTK positioning</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>📡 Telecom</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>HF radio, satellite communications</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>🛡️ Defense</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)' }}>OTH radar, secure comms, navigation</div>
                </div>
              </div>
            </ExpandableInfoPanel>

            {/* Footer */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '20px',
              marginTop: '30px',
              padding: '20px',
              background: 'rgba(0, 20, 40, 0.4)',
              borderRadius: '12px',
              border: '1px solid rgba(74, 144, 226, 0.2)'
            }}>
              <div style={{ textAlign: 'center' }}>
                <h4 style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '8px', textTransform: 'uppercase' }}>
                  Data Sources
                </h4>
                <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>
                  NOAA SWPC • NASA CDDIS
                </p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <h4 style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '8px', textTransform: 'uppercase' }}>
                  Model
                </h4>
                <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>
                  {prediction?.model_version || 'CNN-LSTM v1.0'}
                </p>
              </div>
              <div style={{ textAlign: 'center' }}>
                <h4 style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginBottom: '8px', textTransform: 'uppercase' }}>
                  Forecast Horizon
                </h4>
                <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>
                  24 Hours
                </p>
              </div>
            </div>
          </>
        )}

        {/* Backtest Workshop View */}
        {activeView === 'backtest' && <BacktestWorkshop />}

        {/* Impact Assessment View */}
        {activeView === 'impact' && <ImpactDashboard />}
      </main>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
