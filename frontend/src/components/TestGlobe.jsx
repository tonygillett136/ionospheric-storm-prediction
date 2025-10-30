/**
 * Minimal Three.js Test Component
 * Progressive complexity to isolate the issue
 */
import React, { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

// Simplest possible mesh
const SimpleSphere = () => {
  const meshRef = useRef();

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="#4a90e2" />
    </mesh>
  );
};

const TestGlobe = () => {
  const [step, setStep] = React.useState(1);
  const [error, setError] = React.useState(null);

  console.log('TestGlobe render, step:', step);

  if (error) {
    return (
      <div style={{
        height: '400px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'rgba(255, 0, 0, 0.1)',
        borderRadius: '12px',
        border: '2px solid red',
        padding: '20px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ color: '#ff6b6b', marginBottom: '8px' }}>Error at Step {step}</h3>
          <p style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>
            {error.message}
          </p>
          <pre style={{
            fontSize: '10px',
            marginTop: '12px',
            textAlign: 'left',
            maxWidth: '600px',
            overflow: 'auto',
            background: 'rgba(0,0,0,0.3)',
            padding: '8px',
            borderRadius: '4px'
          }}>
            {error.stack}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '16px', display: 'flex', gap: '8px', alignItems: 'center' }}>
        <h3>Three.js Debug - Step {step}</h3>
        <button
          onClick={() => setStep(Math.max(1, step - 1))}
          style={{ padding: '4px 12px', cursor: 'pointer' }}
        >
          Previous
        </button>
        <button
          onClick={() => setStep(Math.min(5, step + 1))}
          style={{ padding: '4px 12px', cursor: 'pointer' }}
        >
          Next
        </button>
      </div>

      <div style={{
        width: '100%',
        height: '400px',
        background: 'rgba(0, 0, 0, 0.3)',
        borderRadius: '12px',
        border: '1px solid rgba(74, 144, 226, 0.3)'
      }}>
        {step === 1 && (
          <div style={{
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#4ade80'
          }}>
            <div>
              <p style={{ fontSize: '24px', marginBottom: '8px' }}>✓ Step 1: Basic Setup</p>
              <p style={{ fontSize: '14px', opacity: 0.7 }}>No Canvas yet, just React rendering</p>
            </div>
          </div>
        )}

        {step === 2 && (
          <Canvas
            style={{ background: '#000511' }}
            onCreated={() => console.log('Canvas created successfully')}
            onError={(err) => {
              console.error('Canvas error:', err);
              setError(err);
            }}
          >
            <ambientLight intensity={0.5} />
          </Canvas>
        )}

        {step === 3 && (
          <Canvas
            style={{ background: '#000511' }}
            camera={{ position: [0, 0, 3], fov: 50 }}
            onCreated={() => console.log('Canvas with camera created')}
            onError={(err) => {
              console.error('Canvas error:', err);
              setError(err);
            }}
          >
            <ambientLight intensity={0.5} />
            <SimpleSphere />
          </Canvas>
        )}

        {step === 4 && (
          <Canvas
            style={{ background: '#000511' }}
            camera={{ position: [0, 0, 3], fov: 50 }}
            onCreated={() => console.log('Canvas with controls created')}
            onError={(err) => {
              console.error('Canvas error:', err);
              setError(err);
            }}
          >
            <ambientLight intensity={0.5} />
            <directionalLight position={[5, 5, 5]} intensity={1} />
            <SimpleSphere />
            <OrbitControls />
          </Canvas>
        )}

        {step === 5 && (
          <Canvas
            style={{ background: '#000511' }}
            camera={{ position: [0, 0, 3], fov: 50 }}
            onCreated={({ gl }) => {
              console.log('Full setup created');
              gl.setClearColor('#000511');
            }}
            onError={(err) => {
              console.error('Canvas error:', err);
              setError(err);
            }}
          >
            <ambientLight intensity={0.4} />
            <directionalLight position={[5, 3, 5]} intensity={1.2} />
            <pointLight position={[-5, -3, -5]} intensity={0.6} color="#4a90e2" />
            <SimpleSphere />
            <OrbitControls
              enableZoom={true}
              enablePan={false}
              minDistance={2}
              maxDistance={6}
            />
          </Canvas>
        )}
      </div>

      <div style={{ marginTop: '12px', fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>
        <p><strong>Step {step}:</strong></p>
        {step === 1 && <p>Basic React rendering without Three.js</p>}
        {step === 2 && <p>Empty Canvas with just ambient light</p>}
        {step === 3 && <p>Canvas + Camera + Simple Sphere</p>}
        {step === 4 && <p>Canvas + Sphere + OrbitControls</p>}
        {step === 5 && <p>Full lighting setup</p>}
      </div>
    </div>
  );
};

export default TestGlobe;
