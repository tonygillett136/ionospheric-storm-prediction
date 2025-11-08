import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import Glossary from './Glossary';
import './ScienceGuide.css';

const ScienceGuide = () => {
  const [activeChapter, setActiveChapter] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentData, setCurrentData] = useState(null);
  const [readChapters, setReadChapters] = useState(new Set());

  // Fetch current data for interactive elements
  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getCurrentTEC();
        setCurrentData(data);
      } catch (error) {
        console.error('Error fetching data for guide:', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5 * 60 * 1000); // Update every 5 min
    return () => clearInterval(interval);
  }, []);

  // Mark chapter as read when scrolled to bottom
  useEffect(() => {
    const handleScroll = (e) => {
      const element = e.target;
      if (element.scrollHeight - element.scrollTop <= element.clientHeight + 100) {
        setReadChapters(prev => new Set(prev).add(activeChapter));
      }
    };

    const content = document.querySelector('.guide-content');
    if (content) {
      content.addEventListener('scroll', handleScroll);
      return () => content.removeEventListener('scroll', handleScroll);
    }
  }, [activeChapter]);

  const chapters = [
    {
      id: 0,
      title: 'What is the Ionosphere?',
      icon: '🌍',
      section: 'Fundamentals',
      time: '8 min',
      summary: 'Discover the electric sky above us - a layer of plasma that shields Earth and enables global communication.'
    },
    {
      id: 1,
      title: 'Total Electron Content',
      icon: '📊',
      section: 'Fundamentals',
      time: '10 min',
      summary: 'Learn why counting electrons in the sky matters for GPS accuracy and how we measure TEC.'
    },
    {
      id: 2,
      title: 'The Sun-Earth Connection',
      icon: '☀️',
      section: 'Fundamentals',
      time: '12 min',
      summary: 'Explore how solar radiation, solar wind, and magnetic fields drive space weather.'
    },
    {
      id: 3,
      title: 'Geomagnetic Indices',
      icon: '📈',
      section: 'Measurements',
      time: '10 min',
      summary: 'Understand Kp and Dst - the thermometers of geomagnetic storms and what they mean for you.'
    },
    {
      id: 4,
      title: 'Ionospheric Storms',
      icon: '⚡',
      section: 'Measurements',
      time: '15 min',
      summary: 'Witness the anatomy of storms from trigger to peak, including historic events that changed the world.'
    },
    {
      id: 5,
      title: 'Why the Ionosphere Varies',
      icon: '🔄',
      section: 'Variability',
      time: '12 min',
      summary: 'Discover dramatic differences between day and night, summer and winter, equator and poles.'
    },
    {
      id: 6,
      title: 'How We Predict',
      icon: '🔮',
      section: 'Prediction',
      time: '15 min',
      summary: 'Peek behind the curtain at climatology, machine learning, and our scientifically-validated methods.'
    },
    {
      id: 7,
      title: 'Risk Assessment',
      icon: '🎯',
      section: 'Prediction',
      time: '8 min',
      summary: 'Decode the color codes - what LOW, MODERATE, HIGH, and EXTREME really mean for operations.'
    },
    {
      id: 8,
      title: 'Real-Time Monitoring',
      icon: '📡',
      section: 'Using the App',
      time: '10 min',
      summary: 'Master the dashboard features and understand what you\'re seeing in the live data streams.'
    },
    {
      id: 9,
      title: 'Historical Analysis',
      icon: '📅',
      section: 'Using the App',
      time: '12 min',
      summary: 'Time travel through space weather with trends, climatology explorer, and the storm gallery.'
    },
    {
      id: 10,
      title: 'Regional Predictions',
      icon: '🌐',
      section: 'Advanced',
      time: '15 min',
      summary: 'Why one forecast doesn\'t fit all - the science behind our 5-region geographic approach.'
    },
    {
      id: 11,
      title: 'Understanding Uncertainty',
      icon: '❓',
      section: 'Advanced',
      time: '10 min',
      summary: 'Learn the limits of prediction and when to trust (or question) the forecast.'
    },
    {
      id: 12,
      title: 'Practical Applications',
      icon: '✈️',
      section: 'Real World',
      time: '18 min',
      summary: 'See how aviation, maritime, agriculture, and power grids depend on ionospheric forecasts.'
    },
    {
      id: 13,
      title: 'The Future',
      icon: '🚀',
      section: 'Looking Ahead',
      time: '10 min',
      summary: 'Explore emerging technologies and how you can contribute to citizen science.'
    },
    {
      id: 14,
      title: 'Glossary',
      icon: '📖',
      section: 'Reference',
      time: '5 min',
      summary: 'Quick reference for 50+ technical terms from ionosphere to ground-induced currents.'
    }
  ];

  // Group chapters by section
  const sections = [...new Set(chapters.map(c => c.section))];
  const chaptersBySection = sections.map(section => ({
    section,
    chapters: chapters.filter(c => c.section === section)
  }));

  // Calculate progress
  const progress = Math.round((readChapters.size / chapters.length) * 100);

  // Interactive data components
  const LiveTECExample = () => {
    if (!currentData) return <div className="loading-data">Loading live data...</div>;

    return (
      <div className="live-data-embed">
        <div className="live-indicator">🔴 LIVE</div>
        <div className="live-stat">
          <div className="stat-label">Current Global TEC</div>
          <div className="stat-value">{currentData.tec_mean?.toFixed(1) || '—'} <span className="unit">TECU</span></div>
          <div className="stat-context">
            Right now, there are approximately <strong>{(currentData.tec_mean * 10).toFixed(0)} quadrillion electrons</strong> in a square-meter column above you!
          </div>
        </div>
      </div>
    );
  };

  const LiveKpExample = () => {
    if (!currentData) return null;

    const kp = currentData.kp_index || 0;
    const getKpColor = (value) => {
      if (value < 3) return '#10b981';
      if (value < 5) return '#fbbf24';
      if (value < 7) return '#f97316';
      if (value < 8) return '#ef4444';
      return '#991b1b';
    };

    const getKpStatus = (value) => {
      if (value < 3) return 'Quiet';
      if (value < 5) return 'Unsettled';
      if (value < 6) return 'Minor Storm (G1)';
      if (value < 7) return 'Moderate Storm (G2)';
      if (value < 8) return 'Strong Storm (G3)';
      if (value < 9) return 'Severe Storm (G4)';
      return 'Extreme Storm (G5)';
    };

    return (
      <div className="live-data-embed">
        <div className="live-indicator">🔴 LIVE</div>
        <div className="kp-gauge">
          <div className="kp-scale">
            {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map(i => (
              <div
                key={i}
                className={`kp-bar ${i <= kp ? 'active' : ''}`}
                style={{
                  backgroundColor: i <= kp ? getKpColor(kp) : '#334155',
                  height: `${(i + 1) * 10}%`
                }}
              >
                {i}
              </div>
            ))}
          </div>
          <div className="kp-info">
            <div className="kp-value" style={{ color: getKpColor(kp) }}>
              Kp {kp.toFixed(1)}
            </div>
            <div className="kp-status">{getKpStatus(kp)}</div>
          </div>
        </div>
      </div>
    );
  };

  const GPSErrorCalculator = () => {
    const [tecInput, setTecInput] = useState(25);
    const gpsError = (tecInput * 0.16).toFixed(1);

    return (
      <div className="interactive-calculator">
        <h4>GPS Error Calculator</h4>
        <div className="calculator-controls">
          <label>
            TEC Value (TECU):
            <input
              type="range"
              min="0"
              max="100"
              value={tecInput}
              onChange={(e) => setTecInput(Number(e.target.value))}
            />
            <span className="range-value">{tecInput}</span>
          </label>
        </div>
        <div className="calculator-result">
          <div className="result-label">Approximate GPS Error:</div>
          <div className="result-value">{gpsError} meters</div>
          <div className="result-context">
            {gpsError < 2 ? '✅ Excellent accuracy' :
             gpsError < 5 ? '⚠️ Slight degradation' :
             gpsError < 10 ? '⚠️ Noticeable errors' :
             gpsError < 15 ? '❌ Major errors' :
             '❌ Potentially unreliable'}
          </div>
        </div>
      </div>
    );
  };

  // Chapter content with interactive elements
  const getChapterContent = (chapterId) => {
    // This would normally load from the markdown file or API
    // For now, returning placeholder that shows structure
    const interactiveElements = {
      1: <LiveTECExample />,
      2: <GPSErrorCalculator />,
      3: <LiveKpExample />
    };

    return (
      <div className="chapter-content">
        <div className="chapter-header">
          <span className="chapter-icon">{chapters[chapterId].icon}</span>
          <h1>{chapters[chapterId].title}</h1>
          <div className="chapter-meta">
            <span className="reading-time">📖 {chapters[chapterId].time} read</span>
            <span className="chapter-section">{chapters[chapterId].section}</span>
          </div>
        </div>

        {/* Interactive element if available */}
        {interactiveElements[chapterId]}

        {/* Markdown content */}
        <div className="markdown-content">
          <p className="lead-paragraph">
            {chapters[chapterId].summary}
          </p>

          {/* Chapter 14: Show full Glossary component */}
          {chapterId === 14 ? (
            <Glossary />
          ) : (
            <>
              {/* Placeholder for actual markdown content from SCIENCE_GUIDE.md */}
              <div className="content-placeholder">
                <div style={{
                  padding: '24px',
                  background: 'rgba(74, 144, 226, 0.1)',
                  borderLeft: '4px solid #4a90e2',
                  borderRadius: '8px',
                  marginBottom: '24px'
                }}>
                  <h3 style={{ marginTop: 0, color: '#4a90e2' }}>📝 Content Integration Note</h3>
                  <p style={{ margin: '12px 0' }}>
                    Full chapter content from <code>docs/SCIENCE_GUIDE.md</code> would be rendered here using ReactMarkdown.
                  </p>
                  <p style={{ margin: '12px 0' }}>
                    To integrate the full 27,000-word guide:
                  </p>
                  <ol style={{ marginLeft: '20px' }}>
                    <li>Parse <code>SCIENCE_GUIDE.md</code> into chapter sections (using heading markers)</li>
                    <li>Load chapter content based on <code>chapterId</code></li>
                    <li>Render with ReactMarkdown in place of this placeholder</li>
                  </ol>
                  <p style={{ margin: '12px 0' }}>
                    See <code>docs/EDUCATIONAL_CONTENT_INDEX.md</code> for complete integration guide.
                  </p>
                </div>

                {/* Example content for some chapters */}
                {chapterId === 1 && (
                  <div className="example-content">
                    <h3>The GPS Connection</h3>
                    <p>Here's the critical part: when GPS signals travel through the ionosphere, they slow down.
                    The more electrons they encounter, the slower they go. This delay causes <strong>positioning errors</strong>.</p>

                    <GPSErrorCalculator />

                    <p className="info-box">
                      <strong>💡 Try it:</strong> Move the slider to see how TEC affects GPS accuracy.
                      During the May 2024 G5 storm, TEC exceeded 45 TECU in auroral regions - that's over 7 meters of error!
                    </p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Navigation */}
        <div className="chapter-navigation">
          {chapterId > 0 && (
            <button
              className="nav-button prev"
              onClick={() => setActiveChapter(chapterId - 1)}
            >
              ← Previous: {chapters[chapterId - 1].title}
            </button>
          )}
          {chapterId < chapters.length - 1 && (
            <button
              className="nav-button next"
              onClick={() => setActiveChapter(chapterId + 1)}
            >
              Next: {chapters[chapterId + 1].title} →
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="science-guide">
      {/* Sidebar Navigation */}
      <div className="guide-sidebar">
        <div className="sidebar-header">
          <h2>📚 Science Guide</h2>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            <span className="progress-text">{progress}% Complete</span>
          </div>
        </div>

        {/* Search */}
        <div className="search-box">
          <input
            type="text"
            placeholder="Search chapters & glossary..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button className="clear-search" onClick={() => setSearchTerm('')}>×</button>
          )}
        </div>

        {/* Chapter List */}
        <div className="chapter-list">
          {chaptersBySection.map(({ section, chapters: sectionChapters }) => (
            <div key={section} className="chapter-section">
              <div className="section-header">{section}</div>
              {sectionChapters
                .filter(chapter =>
                  !searchTerm ||
                  chapter.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  chapter.summary.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map(chapter => (
                  <div
                    key={chapter.id}
                    className={`chapter-item ${activeChapter === chapter.id ? 'active' : ''} ${readChapters.has(chapter.id) ? 'read' : ''}`}
                    onClick={() => setActiveChapter(chapter.id)}
                  >
                    <span className="chapter-icon">{chapter.icon}</span>
                    <div className="chapter-info">
                      <div className="chapter-title">{chapter.title}</div>
                      <div className="chapter-time">{chapter.time}</div>
                    </div>
                    {readChapters.has(chapter.id) && <span className="read-badge">✓</span>}
                  </div>
                ))}
            </div>
          ))}
        </div>

        {/* Quick Links */}
        <div className="quick-links">
          <h3>Quick Links</h3>
          <a href="#quick-start" className="quick-link">⚡ Quick Start Guide</a>
          <a href="#glossary" className="quick-link" onClick={() => setActiveChapter(14)}>📖 Glossary</a>
          <a href="#diagrams" className="quick-link">🎨 Diagrams</a>
        </div>
      </div>

      {/* Main Content */}
      <div className="guide-content">
        {getChapterContent(activeChapter)}
      </div>

      {/* Right Sidebar - Context Help */}
      <div className="guide-context">
        <div className="context-card">
          <h3>💡 Quick Tip</h3>
          <p>Click terms in <span className="highlight">yellow</span> to see definitions from the glossary.</p>
        </div>

        {currentData && (
          <div className="context-card live-stats">
            <h3>🔴 Live Conditions</h3>
            <div className="stat-row">
              <span className="stat-label">TEC:</span>
              <span className="stat-value">{currentData.tec_mean?.toFixed(1) || '—'} TECU</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Kp:</span>
              <span className="stat-value">{currentData.kp_index?.toFixed(1) || '—'}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Solar Wind:</span>
              <span className="stat-value">{currentData.solar_wind_speed || '—'} km/s</span>
            </div>
            <button className="view-dashboard">View Full Dashboard →</button>
          </div>
        )}

        <div className="context-card">
          <h3>🎯 Related Topics</h3>
          <ul className="related-links">
            {activeChapter === 1 && (
              <>
                <li onClick={() => setActiveChapter(2)}>→ How We Measure TEC</li>
                <li onClick={() => setActiveChapter(7)}>→ Risk Assessment</li>
              </>
            )}
            {activeChapter === 6 && (
              <>
                <li onClick={() => setActiveChapter(10)}>→ Regional Predictions</li>
                <li onClick={() => setActiveChapter(11)}>→ Understanding Uncertainty</li>
              </>
            )}
          </ul>
        </div>

        <div className="context-card">
          <h3>📚 Resources</h3>
          <ul className="resource-links">
            <li><a href="/api/docs" target="_blank">API Documentation</a></li>
            <li><a href="https://github.com/..." target="_blank">View on GitHub</a></li>
            <li><a href="/scientific-review" target="_blank">Scientific Review</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ScienceGuide;
