/**
 * Simple 3D Globe Component with TEC Visualization
 * Lightweight version that's more stable
 */
import React, { useRef, useEffect, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

const EarthGlobe = ({ tecData }) => {
  const globeRef = useRef();
  const pointCloudRef = useRef();

  // Auto-rotate
  useFrame(() => {
    if (globeRef.current) {
      globeRef.current.rotation.y += 0.002;
    }
  });

  // Create TEC point cloud
  const tecPointsGeometry = useMemo(() => {
    if (!tecData || !tecData.tec_values) return null;

    const geometry = new THREE.BufferGeometry();
    const positions = [];
    const colors = [];

    const { latitudes, longitudes, tec_values } = tecData;

    // Sample every 3rd point to reduce complexity
    for (let latIdx = 0; latIdx < latitudes.length; latIdx += 3) {
      for (let lonIdx = 0; lonIdx < longitudes.length; lonIdx += 3) {
        const lat = latitudes[latIdx];
        const lon = longitudes[lonIdx];
        const tecValue = tec_values[latIdx][lonIdx];

        // Convert lat/lon to 3D coordinates
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        const radius = 1.05; // Just above Earth surface

        const x = -radius * Math.sin(phi) * Math.cos(theta);
        const y = radius * Math.cos(phi);
        const z = radius * Math.sin(phi) * Math.sin(theta);

        positions.push(x, y, z);

        // Color based on TEC value
        const color = getTECColor(tecValue);
        colors.push(color.r, color.g, color.b);
      }
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, [tecData]);

  const getTECColor = (tecValue) => {
    // Map TEC values (0-60 TECU) to color gradient
    const normalized = Math.min(tecValue / 60, 1);

    if (normalized < 0.2) {
      return { r: 0.1, g: 0.3, b: 0.9 }; // Blue (low)
    } else if (normalized < 0.4) {
      return { r: 0.1, g: 0.7, b: 0.9 }; // Cyan
    } else if (normalized < 0.6) {
      return { r: 0.9, g: 0.9, b: 0.2 }; // Yellow
    } else if (normalized < 0.8) {
      return { r: 0.95, g: 0.5, b: 0.1 }; // Orange
    } else {
      return { r: 0.95, g: 0.1, b: 0.1 }; // Red (high)
    }
  };

  return (
    <group ref={globeRef}>
      {/* Earth sphere */}
      <mesh>
        <sphereGeometry args={[1, 64, 64]} />
        <meshStandardMaterial
          color="#2b5876"
          roughness={0.7}
          metalness={0.3}
        />
      </mesh>

      {/* Continents (simplified) */}
      <mesh>
        <sphereGeometry args={[1.001, 64, 64]} />
        <meshStandardMaterial
          color="#1a4d2e"
          roughness={0.9}
          metalness={0.1}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* TEC Data Points */}
      {tecPointsGeometry && (
        <points ref={pointCloudRef} geometry={tecPointsGeometry}>
          <pointsMaterial
            size={0.02}
            vertexColors
            transparent
            opacity={0.85}
            sizeAttenuation
          />
        </points>
      )}

      {/* Atmosphere glow */}
      <mesh scale={1.12}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial
          color="#4a90e2"
          transparent
          opacity={0.15}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  );
};

const SimpleGlobe3D = ({ tecData }) => {
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    // Catch any errors during component lifecycle
    const handleError = (event) => {
      console.error('Globe error:', event.error);
      setError(event.error || new Error('3D rendering error'));
    };
    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (error) {
    return (
      <div style={{
        height: '600px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '12px',
        border: '1px dashed rgba(255, 107, 107, 0.5)'
      }}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <p style={{ color: '#ff6b6b' }}>3D visualization unavailable</p>
          <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.5)', marginTop: '8px' }}>
            {error?.message || 'Unknown error'}
          </p>
        </div>
      </div>
    );
  }

  try {
    return (
      <div style={{ width: '100%', height: '600px', position: 'relative' }}>
        <Canvas
          camera={{ position: [0, 0, 2.5], fov: 50 }}
          onCreated={({ gl }) => {
            try {
              gl.setClearColor('#000511');
            } catch (err) {
              console.error('WebGL setup error:', err);
            }
          }}
          onError={(err) => {
            console.error('Canvas error:', err);
            setError(err);
          }}
        >
        {/* Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 3, 5]} intensity={1.2} color="#ffffff" />
        <pointLight position={[-5, -3, -5]} intensity={0.6} color="#4a90e2" />

        {/* Stars */}
        <StarField />

        {/* Globe with TEC data */}
        {tecData ? (
          <EarthGlobe tecData={tecData} />
        ) : (
          <mesh>
            <sphereGeometry args={[1, 64, 64]} />
            <meshStandardMaterial color="#2b5876" />
          </mesh>
        )}

        {/* Camera controls */}
        <OrbitControls
          enableZoom={true}
          enablePan={false}
          minDistance={1.8}
          maxDistance={6}
          autoRotate={false}
          rotateSpeed={0.5}
        />
      </Canvas>

      {/* Controls hint */}
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '10px 14px',
        borderRadius: '8px',
        fontSize: '11px',
        color: 'rgba(255,255,255,0.8)'
      }}>
        <div>🖱️ Drag to rotate</div>
        <div>🔍 Scroll to zoom</div>
      </div>

      {/* TEC Legend */}
      <div style={{
        position: 'absolute',
        bottom: '16px',
        right: '16px',
        background: 'rgba(0, 0, 0, 0.8)',
        padding: '12px',
        borderRadius: '8px',
        fontSize: '11px',
      }}>
        <div style={{ marginBottom: '6px', fontWeight: 'bold', fontSize: '12px' }}>
          TEC Scale (TECU)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
          <div style={{ width: '16px', height: '10px', background: 'rgb(25, 76, 230)', borderRadius: '2px' }} />
          <span>0-12 Low</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
          <div style={{ width: '16px', height: '10px', background: 'rgb(25, 178, 230)', borderRadius: '2px' }} />
          <span>12-24</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
          <div style={{ width: '16px', height: '10px', background: 'rgb(230, 230, 51)', borderRadius: '2px' }} />
          <span>24-36</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}>
          <div style={{ width: '16px', height: '10px', background: 'rgb(242, 127, 25)', borderRadius: '2px' }} />
          <span>36-48</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <div style={{ width: '16px', height: '10px', background: 'rgb(242, 25, 25)', borderRadius: '2px' }} />
          <span>48+ High</span>
        </div>
      </div>

      {/* Data info */}
      {tecData && (
        <div style={{
          position: 'absolute',
          top: '16px',
          right: '16px',
          background: 'rgba(0, 0, 0, 0.7)',
          padding: '10px 14px',
          borderRadius: '8px',
          fontSize: '11px',
          color: 'rgba(255,255,255,0.8)',
          textAlign: 'right'
        }}>
          <div style={{ color: '#4ade80', fontWeight: 'bold' }}>✓ Live TEC Data</div>
          <div style={{ fontSize: '10px', marginTop: '4px', color: 'rgba(255,255,255,0.6)' }}>
            {tecData.latitudes?.length || 0} × {tecData.longitudes?.length || 0} grid
          </div>
        </div>
      )}
    </div>
  );
};

// Star field component
const StarField = () => {
  const starsRef = useRef();

  const starPositions = useMemo(() => {
    const positions = [];
    for (let i = 0; i < 1000; i++) {
      const x = (Math.random() - 0.5) * 100;
      const y = (Math.random() - 0.5) * 100;
      const z = (Math.random() - 0.5) * 100;
      positions.push(x, y, z);
    }
    return new Float32Array(positions);
  }, []);

  useFrame(() => {
    if (starsRef.current) {
      starsRef.current.rotation.y += 0.0001;
    }
  });

  return (
    <points ref={starsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={starPositions.length / 3}
          array={starPositions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.1}
        color="#ffffff"
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
};

export default SimpleGlobe3D;
