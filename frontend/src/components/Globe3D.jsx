/**
 * Fixed 3D Globe Component with TEC Visualization
 * Optimized to prevent re-render issues
 */
import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { TextureLoader } from 'three';

// Move helper functions outside component to prevent recreation
const getTECColor = (tecValue) => {
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

// Earth sphere with texture
const EarthSphere = () => {
  // Use a public Earth texture from NASA
  const earthTexture = useLoader(
    TextureLoader,
    'https://raw.githubusercontent.com/turban/webgl-earth/master/images/2_no_clouds_4k.jpg'
  );

  return (
    <mesh>
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial
        map={earthTexture}
        roughness={0.7}
        metalness={0.1}
      />
    </mesh>
  );
};

const EarthGlobe = ({ tecData }) => {
  const globeRef = useRef();

  // Auto-rotate
  useFrame(() => {
    if (globeRef.current) {
      globeRef.current.rotation.y += 0.002;
    }
  });

  // Create TEC point cloud - memoized properly
  const tecPointsGeometry = useMemo(() => {
    if (!tecData || !tecData.tec_values || !tecData.latitudes || !tecData.longitudes) {
      console.log('No TEC data available for visualization');
      return null;
    }

    console.log('Creating TEC geometry with', tecData.latitudes.length, 'x', tecData.longitudes.length, 'points');

    const geometry = new THREE.BufferGeometry();
    const positions = [];
    const colors = [];
    const sizes = [];

    const { latitudes, longitudes, tec_values } = tecData;

    // Sample every 2nd point for better coverage
    for (let latIdx = 0; latIdx < latitudes.length; latIdx += 2) {
      for (let lonIdx = 0; lonIdx < longitudes.length; lonIdx += 2) {
        const lat = latitudes[latIdx];
        const lon = longitudes[lonIdx];
        const tecValue = tec_values[latIdx][lonIdx];

        // Skip invalid values
        if (tecValue == null || isNaN(tecValue)) continue;

        // Convert lat/lon to 3D coordinates
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        const radius = 1.08; // Raised higher above Earth surface for visibility

        const x = -radius * Math.sin(phi) * Math.cos(theta);
        const y = radius * Math.cos(phi);
        const z = radius * Math.sin(phi) * Math.sin(theta);

        positions.push(x, y, z);

        // Color based on TEC value
        const color = getTECColor(tecValue);
        colors.push(color.r, color.g, color.b);

        // Variable size based on TEC value for emphasis
        sizes.push(0.5 + (tecValue / 60) * 1.5);
      }
    }

    console.log('Created', positions.length / 3, 'TEC points');

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));

    return geometry;
  }, [tecData?.latitudes?.length, tecData?.longitudes?.length, tecData?.tec_values]);

  return (
    <group ref={globeRef}>
      {/* Earth with realistic texture */}
      <Suspense fallback={
        <mesh>
          <sphereGeometry args={[1, 64, 64]} />
          <meshStandardMaterial color="#1a4d2e" />
        </mesh>
      }>
        <EarthSphere />
      </Suspense>

      {/* Latitude/Longitude grid for geographic reference */}
      <mesh>
        <sphereGeometry args={[1.01, 24, 24]} />
        <meshBasicMaterial
          color="#ffffff"
          wireframe={true}
          transparent
          opacity={0.15}
        />
      </mesh>

      {/* Equator line - prominent */}
      <mesh rotation={[0, 0, 0]}>
        <torusGeometry args={[1.012, 0.004, 8, 100]} />
        <meshBasicMaterial color="#ffff00" transparent opacity={0.5} />
      </mesh>

      {/* Prime meridian line */}
      <mesh rotation={[0, 0, Math.PI / 2]}>
        <torusGeometry args={[1.012, 0.004, 8, 100]} />
        <meshBasicMaterial color="#ffff00" transparent opacity={0.4} />
      </mesh>

      {/* TEC Data Points - larger and more prominent */}
      {tecPointsGeometry && (
        <points geometry={tecPointsGeometry}>
          <pointsMaterial
            size={0.06}
            vertexColors
            transparent
            opacity={0.9}
            sizeAttenuation
          />
        </points>
      )}

      {/* Atmosphere glow */}
      <mesh scale={1.15}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color="#4a90e2" transparent opacity={0.1} side={THREE.BackSide} />
      </mesh>
    </group>
  );
};

const StarField = () => {
  const starsRef = useRef();
  const starPositions = useMemo(() => {
    const positions = [];
    for (let i = 0; i < 1000; i++) {
      positions.push((Math.random() - 0.5) * 100, (Math.random() - 0.5) * 100, (Math.random() - 0.5) * 100);
    }
    return new Float32Array(positions);
  }, []);

  useFrame(() => {
    if (starsRef.current) starsRef.current.rotation.y += 0.0001;
  });

  return (
    <points ref={starsRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={starPositions.length / 3} array={starPositions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.1} color="#ffffff" transparent opacity={0.8} sizeAttenuation />
    </points>
  );
};

const Globe3D = ({ tecData }) => {
  const [error, setError] = React.useState(null);

  if (error) {
    return (
      <div style={{ height: '600px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0, 0, 0, 0.3)', borderRadius: '12px', border: '1px dashed rgba(255, 107, 107, 0.5)' }}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <p style={{ color: '#ff6b6b' }}>3D visualization error</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
      <Canvas camera={{ position: [0, 0, 2.5], fov: 50 }} onCreated={({ gl }) => gl.setClearColor('#000511')} onError={(err) => setError(err)}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[5, 3, 5]} intensity={1.2} />
        <pointLight position={[-5, -3, -5]} intensity={0.6} color="#4a90e2" />
        <StarField />
        <EarthGlobe tecData={tecData} />
        <OrbitControls enableZoom enablePan={false} minDistance={1.8} maxDistance={6} rotateSpeed={0.5} />
      </Canvas>
      <div style={{ position: 'absolute', top: '16px', left: '16px', background: 'rgba(0, 0, 0, 0.7)', padding: '10px 14px', borderRadius: '8px', fontSize: '11px', color: 'rgba(255,255,255,0.8)' }}>
        <div>🖱️ Drag to rotate</div>
        <div>🔍 Scroll to zoom</div>
      </div>
      <div style={{ position: 'absolute', bottom: '16px', right: '16px', background: 'rgba(0, 0, 0, 0.8)', padding: '12px', borderRadius: '8px', fontSize: '11px' }}>
        <div style={{ marginBottom: '6px', fontWeight: 'bold', fontSize: '12px' }}>TEC Scale (TECU)</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}><div style={{ width: '16px', height: '10px', background: 'rgb(25, 76, 230)', borderRadius: '2px' }} /><span>0-12 Low</span></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}><div style={{ width: '16px', height: '10px', background: 'rgb(25, 178, 230)', borderRadius: '2px' }} /><span>12-24</span></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}><div style={{ width: '16px', height: '10px', background: 'rgb(230, 230, 51)', borderRadius: '2px' }} /><span>24-36</span></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px' }}><div style={{ width: '16px', height: '10px', background: 'rgb(242, 127, 25)', borderRadius: '2px' }} /><span>36-48</span></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: '16px', height: '10px', background: 'rgb(242, 25, 25)', borderRadius: '2px' }} /><span>48+ High</span></div>
      </div>
      {tecData && (
        <div style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(0, 0, 0, 0.7)', padding: '10px 14px', borderRadius: '8px', fontSize: '11px', color: 'rgba(255,255,255,0.8)', textAlign: 'right' }}>
          <div style={{ color: '#4ade80', fontWeight: 'bold' }}>✓ Live TEC Data</div>
          <div style={{ fontSize: '10px', marginTop: '4px', color: 'rgba(255,255,255,0.6)' }}>{tecData.latitudes?.length || 0} × {tecData.longitudes?.length || 0} grid</div>
        </div>
      )}
    </div>
  );
};

export default Globe3D;
