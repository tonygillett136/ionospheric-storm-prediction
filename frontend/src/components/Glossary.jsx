/**
 * Glossary Component
 * Comprehensive glossary of ionospheric and space weather terms
 */
import React, { useState } from 'react';

const GLOSSARY_TERMS = [
  {
    term: "TEC (Total Electron Content)",
    category: "Ionospheric",
    definition: "The total number of electrons present along a path between a satellite and a receiver on Earth. Measured in TECU (TEC Units), where 1 TECU = 10¹⁶ electrons/m². TEC values typically range from 2-10 TECU at night to 10-100+ TECU during the day, with higher values near the equator."
  },
  {
    term: "TECU (TEC Unit)",
    category: "Measurement",
    definition: "Standard unit for measuring Total Electron Content. 1 TECU equals 10¹⁶ electrons per square meter along the signal path."
  },
  {
    term: "Kp Index",
    category: "Geomagnetic",
    definition: "A global geomagnetic activity index ranging from 0 to 9, updated every 3 hours. It indicates disturbances in Earth's magnetic field: 0-2 = quiet, 3-4 = unsettled, 5 = minor storm (G1), 6 = moderate storm (G2), 7 = strong storm (G3), 8 = severe storm (G4), 9 = extreme storm (G5)."
  },
  {
    term: "Dst Index",
    category: "Geomagnetic",
    definition: "Disturbance Storm Time index measuring the ring current around Earth. Negative values indicate geomagnetic storms: 0 to -30 nT = weak storm, -30 to -50 nT = moderate, -50 to -100 nT = intense, < -100 nT = super-storm."
  },
  {
    term: "IMF (Interplanetary Magnetic Field)",
    category: "Solar Wind",
    definition: "The magnetic field carried by the solar wind through interplanetary space. Its orientation relative to Earth's magnetic field determines how efficiently solar wind energy transfers into the magnetosphere."
  },
  {
    term: "IMF Bz",
    category: "Solar Wind",
    definition: "The north-south component of the Interplanetary Magnetic Field. When Bz is southward (negative), it enables magnetic reconnection with Earth's field, triggering geomagnetic storms. Values < -10 nT indicate strong storm potential."
  },
  {
    term: "Solar Wind",
    category: "Solar",
    definition: "A stream of charged particles (mainly protons and electrons) continuously flowing from the Sun. Normal speed: 300-500 km/s. High-speed streams from coronal holes: 600-800 km/s. CME-driven shocks: >1000 km/s."
  },
  {
    term: "F10.7 Solar Flux",
    category: "Solar",
    definition: "Radio emissions from the Sun at 10.7 cm wavelength (2800 MHz), measured in Solar Flux Units (sfu). Serves as a proxy for solar activity and UV radiation. Typical range: 60-90 sfu (solar minimum) to 150-300 sfu (solar maximum)."
  },
  {
    term: "Ionosphere",
    category: "Atmospheric",
    definition: "A region of Earth's upper atmosphere (50-1000 km altitude) ionized by solar radiation. Contains layers (D, E, F1, F2) with varying electron density that affect radio wave propagation and GPS signals."
  },
  {
    term: "Ionospheric Storm",
    category: "Ionospheric",
    definition: "A large-scale disturbance in ionospheric electron density caused by geomagnetic storms. Can cause TEC depletions or enhancements, GPS errors, HF radio disruptions, and satellite communication issues lasting hours to days."
  },
  {
    term: "GNSS (Global Navigation Satellite System)",
    category: "Technology",
    definition: "Generic term for satellite navigation systems like GPS, GLONASS, Galileo, and BeiDou. Ionospheric delays are a major error source for GNSS positioning."
  },
  {
    term: "ROTI (Rate of TEC Index)",
    category: "Ionospheric",
    definition: "Measures the rate of change of TEC, used as a proxy for ionospheric scintillation. High ROTI values indicate irregular ionospheric structures that can cause signal fading."
  },
  {
    term: "Scintillation",
    category: "Ionospheric",
    definition: "Rapid fluctuations in GNSS signal amplitude and phase caused by ionospheric irregularities. Measured by S4 index (amplitude) and σφ (phase). Most severe in equatorial and polar regions."
  },
  {
    term: "CME (Coronal Mass Ejection)",
    category: "Solar",
    definition: "A massive burst of solar plasma and magnetic field ejected from the Sun's corona. Can reach Earth in 15-18 hours to several days, potentially causing severe geomagnetic storms."
  },
  {
    term: "Solar Flare",
    category: "Solar",
    definition: "A sudden flash of increased brightness on the Sun, releasing intense radiation across the electromagnetic spectrum. Classified as A, B, C, M, or X (increasing intensity). X-class flares can cause radio blackouts."
  },
  {
    term: "Magnetosphere",
    category: "Geomagnetic",
    definition: "The region around Earth dominated by its magnetic field, extending ~60,000 km on the sunward side. Shields Earth from most solar wind particles but can be disturbed during geomagnetic storms."
  },
  {
    term: "Geomagnetic Storm",
    category: "Geomagnetic",
    definition: "A major disturbance of Earth's magnetosphere caused by solar wind shocks or CME impacts. Classified G1-G5 by severity. Effects include auroras, power grid disruptions, satellite anomalies, and GPS errors."
  },
  {
    term: "Plasma Bubble",
    category: "Ionospheric",
    definition: "Large-scale depletion in ionospheric plasma density in equatorial regions. Forms after sunset, rises to high altitudes, and causes severe GNSS scintillation."
  },
  {
    term: "F2 Layer",
    category: "Ionospheric",
    definition: "The highest and most important ionospheric layer (200-400 km altitude) with peak electron density. Most TEC comes from this layer. Highly variable with solar activity, season, and local time."
  },
  {
    term: "GIC (Geomagnetically Induced Current)",
    category: "Space Weather Impact",
    definition: "Electric currents induced in power grids, pipelines, and railways during geomagnetic storms. Can damage transformers and cause power blackouts, especially at high latitudes."
  },
  {
    term: "Space Weather",
    category: "General",
    definition: "Environmental conditions in space influenced by solar activity. Includes solar flares, CMEs, solar wind variations, and their effects on Earth's magnetosphere, ionosphere, and technological systems."
  },
  {
    term: "SWPC (Space Weather Prediction Center)",
    category: "Organization",
    definition: "NOAA's center providing space weather alerts, watches, and warnings. Issues forecasts for solar activity, geomagnetic storms, and ionospheric disturbances."
  },
  {
    term: "VTEC (Vertical TEC)",
    category: "Measurement",
    definition: "Total Electron Content measured vertically from ground to satellite altitude. Converted from slant TEC measurements using mapping functions."
  },
  {
    term: "CNN (Convolutional Neural Network)",
    category: "Machine Learning",
    definition: "A deep learning architecture particularly effective at identifying spatial patterns in data. Used in this system to extract patterns from ionospheric measurements."
  },
  {
    term: "LSTM (Long Short-Term Memory)",
    category: "Machine Learning",
    definition: "A type of recurrent neural network capable of learning long-term temporal dependencies. Used in this system to capture time-series patterns in space weather data."
  }
];

const Glossary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedTerm, setExpandedTerm] = useState(null);

  const categories = ['all', ...new Set(GLOSSARY_TERMS.map(t => t.category))].sort();

  const filteredTerms = GLOSSARY_TERMS.filter(term => {
    const matchesSearch = term.term.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         term.definition.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || term.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }).sort((a, b) => a.term.localeCompare(b.term));

  return (
    <div style={{
      background: 'rgba(0, 20, 40, 0.6)',
      borderRadius: '16px',
      padding: '24px',
      border: '1px solid rgba(74, 144, 226, 0.3)',
      marginBottom: '20px'
    }}>
      <h2 style={{ fontSize: '20px', marginBottom: '20px' }}>Glossary of Terms</h2>

      {/* Search and Filter */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search terms..."
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
            cursor: 'pointer'
          }}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat}
            </option>
          ))}
        </select>
      </div>

      {/* Results Count */}
      <div style={{ marginBottom: '16px', fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
        Showing {filteredTerms.length} of {GLOSSARY_TERMS.length} terms
      </div>

      {/* Terms List */}
      <div style={{ display: 'grid', gap: '12px' }}>
        {filteredTerms.map((item, index) => (
          <div
            key={index}
            style={{
              background: 'rgba(0, 20, 40, 0.4)',
              borderRadius: '8px',
              padding: '16px',
              border: '1px solid rgba(74, 144, 226, 0.3)',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onClick={() => setExpandedTerm(expandedTerm === index ? null : index)}
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
                {expandedTerm === index ? '−' : '+'}
              </span>
            </div>

            {expandedTerm === index && (
              <div style={{
                marginTop: '12px',
                paddingTop: '12px',
                borderTop: '1px solid rgba(74, 144, 226, 0.2)',
                fontSize: '14px',
                lineHeight: '1.6',
                color: 'rgba(255,255,255,0.85)'
              }}>
                {item.definition}
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
