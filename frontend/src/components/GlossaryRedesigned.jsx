/**
 * Redesigned Glossary Component
 * Terms grouped by category with better visual organization
 */
import React, { useState, useMemo } from 'react';

const GLOSSARY_DATA = {
  'Core Concepts': [
    {
      term: "Ionosphere",
      definition: "The region of Earth's upper atmosphere (50-1,000 km) where solar radiation ionizes atmospheric gases, creating free electrons and ions. Acts as a reflector for radio waves and causes delays in GPS signals."
    },
    {
      term: "Total Electron Content (TEC)",
      definition: "The total number of free electrons in a 1 m² column through the ionosphere, measured in TECU (1 TECU = 10¹⁶ electrons/m²). Directly related to GPS signal delay.",
      formula: "GPS error ≈ 0.16 × TEC (meters)"
    },
    {
      term: "Photoionization",
      definition: "The process where high-energy photons (ultraviolet and X-rays) from the Sun knock electrons off atmospheric atoms, creating ions and free electrons."
    },
    {
      term: "Plasma",
      definition: "The fourth state of matter (after solid, liquid, gas), consisting of ionized gas with free electrons and ions. The ionosphere is a natural plasma."
    }
  ],
  'Geomagnetic Indices': [
    {
      term: "Kp Index",
      definition: "A global measure of geomagnetic activity on a 0-9 scale, updated every 3 hours. Kp 0-2 is quiet, Kp 5 is a minor storm, Kp 9 is extreme. Based on magnetometer measurements from 13 stations worldwide.",
      scale: "0-2: Quiet | 3-4: Unsettled | 5: Minor storm | 6: Moderate | 7: Strong | 8-9: Severe/Extreme"
    },
    {
      term: "Dst Index",
      definition: "Measures the intensity of the ring current around Earth during geomagnetic storms, given in nanotesla (nT). Negative values indicate storms (e.g., Dst = -100 nT is a moderate storm). Updated hourly."
    },
    {
      term: "G-Scale",
      definition: "NOAA's 5-level storm classification: G1 (minor, Kp 5), G2 (moderate, Kp 6), G3 (strong, Kp 7), G4 (severe, Kp 8), G5 (extreme, Kp 9)."
    }
  ],
  'Solar Phenomena': [
    {
      term: "Solar Wind",
      definition: "A continuous stream of charged particles (mainly protons and electrons) flowing from the Sun at 300-800 km/s. Carries the interplanetary magnetic field and energy that drives space weather."
    },
    {
      term: "Coronal Mass Ejection (CME)",
      definition: "A massive eruption of plasma and magnetic field from the Sun's corona. Can reach Earth in 1-3 days and trigger severe geomagnetic storms."
    },
    {
      term: "Solar Flare",
      definition: "A sudden burst of electromagnetic radiation from the Sun's surface. X-class flares are the most intense. Often accompanies CMEs but travels at light speed (8 minutes to Earth)."
    },
    {
      term: "F10.7 Flux",
      definition: "Solar radio emission at 10.7 cm wavelength, measured in Solar Flux Units (SFU). A proxy for extreme ultraviolet radiation that ionizes the atmosphere. Values range from ~70 (solar minimum) to 300+ (solar maximum)."
    },
    {
      term: "Solar Cycle",
      definition: "The ~11-year cycle of solar activity, from minimum (few sunspots) to maximum (many sunspots) and back. Currently in Cycle 25 (began December 2019)."
    }
  ],
  'Magnetic Field': [
    {
      term: "IMF (Interplanetary Magnetic Field)",
      definition: "The magnetic field carried by the solar wind. Originates from the Sun and extends throughout the solar system."
    },
    {
      term: "IMF Bz",
      definition: "The north-south component of the IMF. When Bz points south (negative), it allows solar wind energy to enter Earth's magnetosphere more efficiently, triggering storms."
    },
    {
      term: "Magnetosphere",
      definition: "The region around Earth dominated by our planet's magnetic field. Acts as a shield against the solar wind, but can be disrupted during storms."
    },
    {
      term: "Ring Current",
      definition: "A doughnut-shaped electric current flowing around Earth during geomagnetic storms, carried by energetic particles trapped in the magnetic field. Creates the Dst index signal."
    },
    {
      term: "Magnetic Reconnection",
      definition: "The process where magnetic field lines from the Sun and Earth connect and 'break and reconnect,' allowing solar wind energy to enter the magnetosphere. Primary driver of geomagnetic storms."
    }
  ],
  'Ionospheric Layers': [
    {
      term: "D Region",
      definition: "Lowest ionospheric layer (50-90 km), exists only during daytime. Absorbs high-frequency (HF) radio waves. Why AM radio propagates farther at night."
    },
    {
      term: "E Region",
      definition: "Middle layer (90-150 km), exists day and night but stronger during day. Reflects some radio frequencies. Contains sporadic E layers."
    },
    {
      term: "F Region",
      definition: "Highest and most important layer (150-500 km). Divided into F1 (150-220 km, daytime only) and F2 (220-500 km, day and night). Contains peak electron density. Most important for GPS and HF communications."
    },
    {
      term: "F2 Peak",
      definition: "The altitude of maximum electron density in the ionosphere, typically 250-350 km. Varies with solar activity, season, and local time."
    }
  ],
  'Prediction Methods': [
    {
      term: "Climatology",
      definition: "Statistical model based on historical averages. Predicts 'normal' behavior for given conditions (day of year, time, Kp level). Very reliable for typical conditions but can't predict unusual events."
    },
    {
      term: "Machine Learning (ML)",
      definition: "Uses neural networks trained on historical data to learn complex patterns and make predictions. Can capture storm dynamics but may fail on extreme events outside training data."
    },
    {
      term: "Ensemble Prediction",
      definition: "Combines multiple models (e.g., climatology + ML) to leverage strengths of each approach. Often more accurate than single models."
    },
    {
      term: "BiLSTM",
      definition: "Bidirectional Long Short-Term Memory - a type of recurrent neural network that processes sequences in both forward and backward time directions. Effective for time series prediction."
    },
    {
      term: "Attention Mechanism",
      definition: "Neural network component that learns to focus on most important features/time steps. Inspired by how humans pay attention. Key technology in modern AI."
    }
  ],
  'Measurement': [
    {
      term: "GNSS",
      definition: "Global Navigation Satellite System - generic term for satellite navigation systems (GPS, Galileo, GLONASS, BeiDou). Used for both navigation and ionospheric TEC measurement."
    },
    {
      term: "Dual-Frequency GNSS",
      definition: "Uses two different radio frequencies to measure ionospheric delay. The frequency-dependent delay allows calculation of TEC."
    },
    {
      term: "Ionosonde",
      definition: "Ground-based radar that bounces radio waves off the ionosphere to measure electron density profiles. Provides altitude information GNSS can't."
    },
    {
      term: "COSMIC",
      definition: "Constellation Observing System for Meteorology, Ionosphere, and Climate - satellite mission that measures ionospheric electron density profiles globally using GPS radio occultation."
    }
  ],
  'Geographic': [
    {
      term: "Latitude",
      definition: "Angular distance north or south from the equator (0° to ±90°). Geographic latitude based on Earth's shape."
    },
    {
      term: "Magnetic Latitude",
      definition: "Latitude in Earth's magnetic coordinate system. Auroral oval defined by magnetic latitude (~65-75°), not geographic."
    },
    {
      term: "AACGM",
      definition: "Altitude-Adjusted Corrected Geomagnetic Coordinates - standard magnetic coordinate system used in space physics. Corrects for ionospheric altitude (e.g., 350 km)."
    },
    {
      term: "Equatorial Anomaly",
      definition: "Also called Appleton Anomaly - the phenomenon where TEC peaks at ±15° latitude rather than at the magnetic equator. Caused by the plasma fountain effect."
    },
    {
      term: "Auroral Oval",
      definition: "Ring-shaped region around magnetic poles where aurora occurs, typically 65-75° magnetic latitude. Expands equatorward during storms."
    }
  ],
  'Statistical': [
    {
      term: "MAE",
      definition: "Mean Absolute Error - average magnitude of prediction errors: mean(|prediction - actual|). In TECU for TEC forecasts. Lower is better."
    },
    {
      term: "RMSE",
      definition: "Root Mean Square Error - square root of average squared errors: sqrt(mean((prediction - actual)²)). Emphasizes large errors more than MAE. Also in TECU."
    },
    {
      term: "Confidence Interval",
      definition: "Range of values likely to contain the true value. E.g., '15 ± 3 TECU with 95% confidence' means 95% chance true value is 12-18 TECU."
    },
    {
      term: "Backtesting",
      definition: "Testing prediction model on historical data not used in training. The gold standard for validating forecast skill."
    }
  ],
  'Practical Impact': [
    {
      term: "GPS Positioning Error",
      definition: "Inaccuracy in calculated position due to various error sources. Ionospheric delay typically contributes 1-10 meters, more during storms."
    },
    {
      term: "RTK",
      definition: "Real-Time Kinematic - high-precision GNSS technique using carrier phase measurements. Achieves centimeter accuracy but very sensitive to ionospheric disturbances."
    },
    {
      term: "HF Radio",
      definition: "High Frequency radio (3-30 MHz) that reflects off the ionosphere, enabling long-distance communication. Disrupted during ionospheric storms."
    },
    {
      term: "Ground-Induced Currents (GIC)",
      definition: "Electric currents flowing through the ground and into power grids during geomagnetic storms. Can damage transformers and cause blackouts."
    },
    {
      term: "Scintillation",
      definition: "Rapid fluctuations in GPS signal strength caused by ionospheric irregularities. Can cause loss of GPS lock."
    }
  ]
};

const GlossaryRedesigned = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState(new Set(Object.keys(GLOSSARY_DATA)));
  const [expandedTerms, setExpandedTerms] = useState(new Set());

  const categories = Object.keys(GLOSSARY_DATA);

  const filteredData = useMemo(() => {
    if (!searchTerm) return GLOSSARY_DATA;

    const filtered = {};
    Object.entries(GLOSSARY_DATA).forEach(([category, terms]) => {
      const matchingTerms = terms.filter(term =>
        term.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
        term.definition.toLowerCase().includes(searchTerm.toLowerCase())
      );
      if (matchingTerms.length > 0) {
        filtered[category] = matchingTerms;
      }
    });
    return filtered;
  }, [searchTerm]);

  const toggleCategory = (category) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleTerm = (termName) => {
    const newExpanded = new Set(expandedTerms);
    if (newExpanded.has(termName)) {
      newExpanded.delete(termName);
    } else {
      newExpanded.add(termName);
    }
    setExpandedTerms(newExpanded);
  };

  const expandAllCategories = () => {
    setExpandedCategories(new Set(Object.keys(filteredData)));
  };

  const collapseAllCategories = () => {
    setExpandedCategories(new Set());
  };

  const totalTerms = Object.values(filteredData).reduce((sum, terms) => sum + terms.length, 0);

  return (
    <div style={{
      background: 'rgba(0, 20, 40, 0.6)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(74, 144, 226, 0.3)',
      marginBottom: '20px'
    }}>
      <h2 style={{ fontSize: '24px', marginBottom: '8px', color: '#4a90e2' }}>📖 Glossary of Terms</h2>
      <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.6)', marginBottom: '20px' }}>
        Comprehensive reference for ionospheric and space weather terminology
      </p>

      {/* Search and Controls */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search all terms..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            minWidth: '250px',
            padding: '12px 16px',
            background: 'rgba(0, 20, 40, 0.6)',
            border: '1px solid rgba(74, 144, 226, 0.4)',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '14px'
          }}
        />
        <button
          onClick={expandAllCategories}
          style={{
            padding: '12px 20px',
            background: 'rgba(74, 144, 226, 0.2)',
            border: '1px solid rgba(74, 144, 226, 0.4)',
            borderRadius: '8px',
            color: '#4a90e2',
            fontSize: '13px',
            cursor: 'pointer',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.target.style.background = 'rgba(74, 144, 226, 0.3)'}
          onMouseOut={(e) => e.target.style.background = 'rgba(74, 144, 226, 0.2)'}
        >
          Expand All
        </button>
        <button
          onClick={collapseAllCategories}
          style={{
            padding: '12px 20px',
            background: 'rgba(0, 20, 40, 0.6)',
            border: '1px solid rgba(74, 144, 226, 0.4)',
            borderRadius: '8px',
            color: 'rgba(255,255,255,0.7)',
            fontSize: '13px',
            cursor: 'pointer',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.target.style.borderColor = 'rgba(74, 144, 226, 0.6)'}
          onMouseOut={(e) => e.target.style.borderColor = 'rgba(74, 144, 226, 0.4)'}
        >
          Collapse All
        </button>
      </div>

      {/* Results Count */}
      <div style={{ marginBottom: '20px', fontSize: '13px', color: 'rgba(255,255,255,0.5)' }}>
        {totalTerms} terms across {Object.keys(filteredData).length} categories
      </div>

      {/* Categories */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {Object.entries(filteredData).map(([category, terms]) => (
          <div
            key={category}
            style={{
              background: 'rgba(0, 20, 40, 0.4)',
              borderRadius: '12px',
              border: '1px solid rgba(74, 144, 226, 0.3)',
              overflow: 'hidden'
            }}
          >
            {/* Category Header */}
            <div
              onClick={() => toggleCategory(category)}
              style={{
                padding: '16px 20px',
                background: expandedCategories.has(category) ? 'rgba(74, 144, 226, 0.15)' : 'rgba(0, 20, 40, 0.3)',
                borderBottom: expandedCategories.has(category) ? '1px solid rgba(74, 144, 226, 0.3)' : 'none',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                transition: 'all 0.2s'
              }}
            >
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#4a90e2', marginBottom: '4px' }}>
                  {category}
                </h3>
                <span style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)' }}>
                  {terms.length} term{terms.length !== 1 ? 's' : ''}
                </span>
              </div>
              <span style={{ fontSize: '20px', color: 'rgba(255,255,255,0.5)' }}>
                {expandedCategories.has(category) ? '−' : '+'}
              </span>
            </div>

            {/* Category Terms */}
            {expandedCategories.has(category) && (
              <div style={{ padding: '12px' }}>
                {terms.map((term, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: 'rgba(0, 20, 40, 0.3)',
                      borderRadius: '8px',
                      padding: '14px 16px',
                      marginBottom: idx < terms.length - 1 ? '8px' : '0',
                      border: `1px solid ${expandedTerms.has(term.term) ? 'rgba(74, 144, 226, 0.4)' : 'rgba(74, 144, 226, 0.2)'}`,
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                    onClick={() => toggleTerm(term.term)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h4 style={{ fontSize: '15px', color: '#4a90e2', margin: 0 }}>
                        {term.term}
                      </h4>
                      <span style={{ fontSize: '18px', color: 'rgba(255,255,255,0.4)' }}>
                        {expandedTerms.has(term.term) ? '−' : '+'}
                      </span>
                    </div>

                    {expandedTerms.has(term.term) && (
                      <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(74, 144, 226, 0.2)' }}>
                        <p style={{ margin: '0', fontSize: '14px', lineHeight: '1.6', color: 'rgba(255,255,255,0.85)' }}>
                          {term.definition}
                        </p>

                        {term.formula && (
                          <div style={{
                            marginTop: '12px',
                            padding: '10px 14px',
                            background: 'rgba(74, 144, 226, 0.1)',
                            borderLeft: '3px solid rgba(74, 144, 226, 0.5)',
                            borderRadius: '4px',
                            fontSize: '13px',
                            fontFamily: 'monospace'
                          }}>
                            <strong style={{ color: '#4a90e2' }}>Formula:</strong> {term.formula}
                          </div>
                        )}

                        {term.scale && (
                          <div style={{
                            marginTop: '12px',
                            padding: '10px 14px',
                            background: 'rgba(74, 144, 226, 0.1)',
                            borderLeft: '3px solid rgba(74, 144, 226, 0.5)',
                            borderRadius: '4px',
                            fontSize: '13px'
                          }}>
                            <strong style={{ color: '#4a90e2' }}>Scale:</strong> {term.scale}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {totalTerms === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: 'rgba(255,255,255,0.5)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
          <p>No terms found matching "{searchTerm}"</p>
          <p style={{ fontSize: '13px', marginTop: '8px' }}>Try a different search term</p>
        </div>
      )}
    </div>
  );
};

export default GlossaryRedesigned;
