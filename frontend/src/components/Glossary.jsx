/**
 * Glossary Component
 * Comprehensive glossary of ionospheric and space weather terms
 */
import React, { useState } from 'react';

const GLOSSARY_TERMS = [
  // Core Concepts
  {
    term: "Ionosphere",
    category: "Core Concepts",
    definition: "The region of Earth's upper atmosphere (50-1,000 km) where solar radiation ionizes atmospheric gases, creating free electrons and ions. Acts as a reflector for radio waves and causes delays in GPS signals."
  },
  {
    term: "Total Electron Content (TEC)",
    category: "Core Concepts",
    definition: "The total number of free electrons in a 1 m² column through the ionosphere, measured in TECU (1 TECU = 10¹⁶ electrons/m²). Directly related to GPS signal delay.",
    formula: "GPS error ≈ 0.16 × TEC (meters)"
  },
  {
    term: "Photoionization",
    category: "Core Concepts",
    definition: "The process where high-energy photons (ultraviolet and X-rays) from the Sun knock electrons off atmospheric atoms, creating ions and free electrons."
  },
  {
    term: "Plasma",
    category: "Core Concepts",
    definition: "The fourth state of matter (after solid, liquid, gas), consisting of ionized gas with free electrons and ions. The ionosphere is a natural plasma."
  },

  // Geomagnetic Indices
  {
    term: "Kp Index",
    category: "Geomagnetic Indices",
    definition: "A global measure of geomagnetic activity on a 0-9 scale, updated every 3 hours. Kp 0-2 is quiet, Kp 5 is a minor storm, Kp 9 is extreme. Based on magnetometer measurements from 13 stations worldwide.",
    scale: "0-2: Quiet | 3-4: Unsettled | 5: Minor storm | 6: Moderate | 7: Strong | 8-9: Severe/Extreme"
  },
  {
    term: "Dst Index",
    category: "Geomagnetic Indices",
    definition: "Measures the intensity of the ring current around Earth during geomagnetic storms, given in nanotesla (nT). Negative values indicate storms (e.g., Dst = -100 nT is a moderate storm). Updated hourly."
  },
  {
    term: "G-Scale",
    category: "Geomagnetic Indices",
    definition: "NOAA's 5-level storm classification: G1 (minor, Kp 5), G2 (moderate, Kp 6), G3 (strong, Kp 7), G4 (severe, Kp 8), G5 (extreme, Kp 9)."
  },

  // Solar Phenomena
  {
    term: "Solar Wind",
    category: "Solar Phenomena",
    definition: "A continuous stream of charged particles (mainly protons and electrons) flowing from the Sun at 300-800 km/s. Carries the interplanetary magnetic field and energy that drives space weather."
  },
  {
    term: "Coronal Mass Ejection (CME)",
    category: "Solar Phenomena",
    definition: "A massive eruption of plasma and magnetic field from the Sun's corona. Can reach Earth in 1-3 days and trigger severe geomagnetic storms."
  },
  {
    term: "Solar Flare",
    category: "Solar Phenomena",
    definition: "A sudden burst of electromagnetic radiation from the Sun's surface. X-class flares are the most intense. Often accompanies CMEs but travels at light speed (8 minutes to Earth)."
  },
  {
    term: "F10.7 Flux",
    category: "Solar Phenomena",
    definition: "Solar radio emission at 10.7 cm wavelength, measured in Solar Flux Units (SFU). A proxy for extreme ultraviolet radiation that ionizes the atmosphere. Values range from ~70 (solar minimum) to 300+ (solar maximum)."
  },
  {
    term: "Solar Cycle",
    category: "Solar Phenomena",
    definition: "The ~11-year cycle of solar activity, from minimum (few sunspots) to maximum (many sunspots) and back. Currently in Cycle 25 (began December 2019)."
  },

  // Magnetic Field Concepts
  {
    term: "IMF (Interplanetary Magnetic Field)",
    category: "Magnetic Field",
    definition: "The magnetic field carried by the solar wind. Originates from the Sun and extends throughout the solar system."
  },
  {
    term: "IMF Bz",
    category: "Magnetic Field",
    definition: "The north-south component of the IMF. When Bz points south (negative), it allows solar wind energy to enter Earth's magnetosphere more efficiently, triggering storms."
  },
  {
    term: "Magnetosphere",
    category: "Magnetic Field",
    definition: "The region around Earth dominated by our planet's magnetic field. Acts as a shield against the solar wind, but can be disrupted during storms."
  },
  {
    term: "Ring Current",
    category: "Magnetic Field",
    definition: "A doughnut-shaped electric current flowing around Earth during geomagnetic storms, carried by energetic particles trapped in the magnetic field. Creates the Dst index signal."
  },
  {
    term: "Magnetic Reconnection",
    category: "Magnetic Field",
    definition: "The process where magnetic field lines from the Sun and Earth connect and 'break and reconnect,' allowing solar wind energy to enter the magnetosphere. Primary driver of geomagnetic storms."
  },

  // Ionospheric Layers
  {
    term: "D Region",
    category: "Ionospheric Layers",
    definition: "Lowest ionospheric layer (50-90 km), exists only during daytime. Absorbs high-frequency (HF) radio waves. Why AM radio propagates farther at night."
  },
  {
    term: "E Region",
    category: "Ionospheric Layers",
    definition: "Middle layer (90-150 km), exists day and night but stronger during day. Reflects some radio frequencies. Contains sporadic E layers."
  },
  {
    term: "F Region",
    category: "Ionospheric Layers",
    definition: "Highest and most important layer (150-500 km). Divided into F1 (150-220 km, daytime only) and F2 (220-500 km, day and night). Contains peak electron density. Most important for GPS and HF communications."
  },
  {
    term: "F2 Peak",
    category: "Ionospheric Layers",
    definition: "The altitude of maximum electron density in the ionosphere, typically 250-350 km. Varies with solar activity, season, and local time."
  },

  // Prediction Methods
  {
    term: "Climatology",
    category: "Prediction Methods",
    definition: "Statistical model based on historical averages. Predicts 'normal' behavior for given conditions (day of year, time, Kp level). Very reliable for typical conditions but can't predict unusual events."
  },
  {
    term: "Machine Learning (ML)",
    category: "Prediction Methods",
    definition: "Uses neural networks trained on historical data to learn complex patterns and make predictions. Can capture storm dynamics but may fail on extreme events outside training data."
  },
  {
    term: "Ensemble Prediction",
    category: "Prediction Methods",
    definition: "Combines multiple models (e.g., climatology + ML) to leverage strengths of each approach. Often more accurate than single models."
  },
  {
    term: "BiLSTM",
    category: "Prediction Methods",
    definition: "Bidirectional Long Short-Term Memory - a type of recurrent neural network that processes sequences in both forward and backward time directions. Effective for time series prediction."
  },
  {
    term: "Attention Mechanism",
    category: "Prediction Methods",
    definition: "Neural network component that learns to focus on most important features/time steps. Inspired by how humans pay attention. Key technology in modern AI."
  },

  // Measurement Techniques
  {
    term: "GNSS",
    category: "Measurement",
    definition: "Global Navigation Satellite System - generic term for satellite navigation systems (GPS, Galileo, GLONASS, BeiDou). Used for both navigation and ionospheric TEC measurement."
  },
  {
    term: "Dual-Frequency GNSS",
    category: "Measurement",
    definition: "Uses two different radio frequencies to measure ionospheric delay. The frequency-dependent delay allows calculation of TEC."
  },
  {
    term: "Ionosonde",
    category: "Measurement",
    definition: "Ground-based radar that bounces radio waves off the ionosphere to measure electron density profiles. Provides altitude information GNSS can't."
  },
  {
    term: "COSMIC",
    category: "Measurement",
    definition: "Constellation Observing System for Meteorology, Ionosphere, and Climate - satellite mission that measures ionospheric electron density profiles globally using GPS radio occultation."
  },

  // Geographic Terms
  {
    term: "Latitude",
    category: "Geographic",
    definition: "Angular distance north or south from the equator (0° to ±90°). Geographic latitude based on Earth's shape."
  },
  {
    term: "Magnetic Latitude",
    category: "Geographic",
    definition: "Latitude in Earth's magnetic coordinate system. Auroral oval defined by magnetic latitude (~65-75°), not geographic."
  },
  {
    term: "AACGM",
    category: "Geographic",
    definition: "Altitude-Adjusted Corrected Geomagnetic Coordinates - standard magnetic coordinate system used in space physics. Corrects for ionospheric altitude (e.g., 350 km)."
  },
  {
    term: "Equatorial Anomaly",
    category: "Geographic",
    definition: "Also called Appleton Anomaly - the phenomenon where TEC peaks at ±15° latitude rather than at the magnetic equator. Caused by the plasma fountain effect."
  },
  {
    term: "Auroral Oval",
    category: "Geographic",
    definition: "Ring-shaped region around magnetic poles where aurora occurs, typically 65-75° magnetic latitude. Expands equatorward during storms."
  },

  // Statistical Terms
  {
    term: "MAE",
    category: "Statistical",
    definition: "Mean Absolute Error - average magnitude of prediction errors: mean(|prediction - actual|). In TECU for TEC forecasts. Lower is better."
  },
  {
    term: "RMSE",
    category: "Statistical",
    definition: "Root Mean Square Error - square root of average squared errors: sqrt(mean((prediction - actual)²)). Emphasizes large errors more than MAE. Also in TECU."
  },
  {
    term: "Confidence Interval",
    category: "Statistical",
    definition: "Range of values likely to contain the true value. E.g., '15 ± 3 TECU with 95% confidence' means 95% chance true value is 12-18 TECU."
  },
  {
    term: "Backtesting",
    category: "Statistical",
    definition: "Testing prediction model on historical data not used in training. The gold standard for validating forecast skill."
  },

  // Practical Impact
  {
    term: "GPS Positioning Error",
    category: "Practical Impact",
    definition: "Inaccuracy in calculated position due to various error sources. Ionospheric delay typically contributes 1-10 meters, more during storms."
  },
  {
    term: "RTK",
    category: "Practical Impact",
    definition: "Real-Time Kinematic - high-precision GNSS technique using carrier phase measurements. Achieves centimeter accuracy but very sensitive to ionospheric disturbances."
  },
  {
    term: "HF Radio",
    category: "Practical Impact",
    definition: "High Frequency radio (3-30 MHz) that reflects off the ionosphere, enabling long-distance communication. Disrupted during ionospheric storms."
  },
  {
    term: "Ground-Induced Currents (GIC)",
    category: "Practical Impact",
    definition: "Electric currents flowing through the ground and into power grids during geomagnetic storms. Can damage transformers and cause blackouts."
  },
  {
    term: "Scintillation",
    category: "Practical Impact",
    definition: "Rapid fluctuations in GPS signal strength caused by ionospheric irregularities. Can cause loss of GPS lock."
  }
];

const Glossary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedTerms, setExpandedTerms] = useState(new Set());

  const categories = ['all', ...new Set(GLOSSARY_TERMS.map(t => t.category))].sort();

  const filteredTerms = GLOSSARY_TERMS.filter(term => {
    const matchesSearch = term.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         term.definition.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || term.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }).sort((a, b) => a.term.localeCompare(b.term));

  const toggleTerm = (termName) => {
    const newExpanded = new Set(expandedTerms);
    if (newExpanded.has(termName)) {
      newExpanded.delete(termName);
    } else {
      newExpanded.add(termName);
    }
    setExpandedTerms(newExpanded);
  };

  const expandAll = () => {
    setExpandedTerms(new Set(filteredTerms.map(item => item.term)));
  };

  const collapseAll = () => {
    setExpandedTerms(new Set());
  };

  return (
    <div style={{
      background: 'rgba(0, 20, 40, 0.6)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(74, 144, 226, 0.3)',
      marginBottom: '20px'
    }}>
      <h2 style={{ fontSize: '20px', marginBottom: '20px' }}>📖 Glossary of Terms</h2>

      {/* Search and Filter */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search terms or definitions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            minWidth: '200px',
            padding: '10px 14px',
            background: 'rgba(0, 20, 40, 0.6)',
            border: '1px solid rgba(74, 144, 226, 0.4)',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '14px'
          }}
        />

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{
            padding: '10px 14px',
            background: 'rgba(0, 20, 40, 0.6)',
            border: '1px solid rgba(74, 144, 226, 0.4)',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '14px',
            cursor: 'pointer',
            minWidth: '150px'
          }}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat}
            </option>
          ))}
        </select>

        <button
          onClick={expandAll}
          style={{
            padding: '10px 16px',
            background: 'rgba(74, 144, 226, 0.3)',
            border: '1px solid rgba(74, 144, 226, 0.5)',
            borderRadius: '8px',
            color: '#4a90e2',
            fontSize: '13px',
            cursor: 'pointer',
            fontWeight: '500',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => e.target.style.background = 'rgba(74, 144, 226, 0.4)'}
          onMouseOut={(e) => e.target.style.background = 'rgba(74, 144, 226, 0.3)'}
        >
          Expand All
        </button>

        <button
          onClick={collapseAll}
          style={{
            padding: '10px 16px',
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
      <div style={{ marginBottom: '16px', fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
        Showing {filteredTerms.length} of {GLOSSARY_TERMS.length} terms
        {expandedTerms.size > 0 && ` • ${expandedTerms.size} expanded`}
      </div>

      {/* Terms List */}
      <div style={{ display: 'grid', gap: '12px' }}>
        {filteredTerms.map((item) => (
          <div
            key={item.term}
            style={{
              background: 'rgba(0, 20, 40, 0.4)',
              borderRadius: '8px',
              padding: '16px',
              border: `1px solid ${expandedTerms.has(item.term) ? 'rgba(74, 144, 226, 0.5)' : 'rgba(74, 144, 226, 0.3)'}`,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onClick={() => toggleTerm(item.term)}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: '16px', color: '#4a90e2', marginBottom: '4px' }}>
                  {item.term}
                </h3>
                <span style={{
                  fontSize: '11px',
                  color: 'rgba(255,255,255,0.5)',
                  background: 'rgba(74, 144, 226, 0.2)',
                  padding: '2px 8px',
                  borderRadius: '4px'
                }}>
                  {item.category}
                </span>
              </div>
              <span style={{ fontSize: '20px', color: 'rgba(255,255,255,0.5)' }}>
                {expandedTerms.has(item.term) ? '−' : '+'}
              </span>
            </div>

            {expandedTerms.has(item.term) && (
              <div style={{
                marginTop: '12px',
                paddingTop: '12px',
                borderTop: '1px solid rgba(74, 144, 226, 0.2)',
                fontSize: '14px',
                lineHeight: '1.6',
                color: 'rgba(255,255,255,0.85)'
              }}>
                <p style={{ margin: '0 0 8px 0' }}>{item.definition}</p>

                {item.formula && (
                  <div style={{
                    marginTop: '12px',
                    padding: '8px 12px',
                    background: 'rgba(74, 144, 226, 0.1)',
                    borderLeft: '3px solid rgba(74, 144, 226, 0.5)',
                    borderRadius: '4px',
                    fontSize: '13px',
                    fontFamily: 'monospace'
                  }}>
                    <strong style={{ color: '#4a90e2' }}>Formula:</strong> {item.formula}
                  </div>
                )}

                {item.scale && (
                  <div style={{
                    marginTop: '12px',
                    padding: '8px 12px',
                    background: 'rgba(74, 144, 226, 0.1)',
                    borderLeft: '3px solid rgba(74, 144, 226, 0.5)',
                    borderRadius: '4px',
                    fontSize: '13px'
                  }}>
                    <strong style={{ color: '#4a90e2' }}>Scale:</strong> {item.scale}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {filteredTerms.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: 'rgba(255,255,255,0.5)'
        }}>
          No terms found matching your search.
        </div>
      )}
    </div>
  );
};

export default Glossary;
