import React from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere } from '@react-three/drei';
import { useMemo } from 'react';

interface HolographicOrbProps {
  vendor: string;
  metrics: {
    frozen?: boolean;
    riskScore?: number;
    riskColor?: string;
    [key: string]: any;
  };
}

const HolographicOrb: React.FC<HolographicOrbProps> = ({ vendor, metrics }) => {
  const { frozen, riskScore, riskColor } = metrics;

  // Determine color and pulse based on vendor and state
  const orbColor = useMemo(() => {
    if (vendor.includes('Vardhaman') && frozen) {
      // Crimson red for frozen state
      return '#EF4444';
    } else if (vendor.includes('SecureLogix')) {
      // Emerald green for SecureLogix
      return '#10B981';
    } else if (vendor.includes('Apex')) {
      // Apex might be blue or green, but we'll use a light green
      return '#34D399';
    } else if (vendor.includes('Matrix')) {
      // Matrix might be a dark cyan or purple
      return '#6366F1';
    } else {
      // Default to the riskColor or cyan
      return riskColor || '#00E5FF';
    }
  }, [vendor, frozen, riskColor]);

  // Pulse effect for frozen state
  const pulse = frozen ? Math.sin(Date.now() * 0.005) * 0.3 + 0.7 : 1;

  // Rotation speed based on riskScore (higher risk -> faster rotation) or vendor
  const baseSpeed = 0.0005;
  const speedMultiplier = useMemo(() => {
    if (riskScore !== undefined) {
      // Map riskScore 0-100 to 0.5 to 2.0
      return 0.5 + (riskScore / 100) * 1.5;
    }
    return 1;
  }, [riskScore]);
  const rotationSpeed = baseSpeed * speedMultiplier;

  // Ref for the sphere to update material
  const sphereRef = React.useRef<any>(null);

  useFrame((state, delta) => {
    if (sphereRef.current) {
      // Rotate the sphere
      sphereRef.current.rotation.x += rotationSpeed * delta;
      sphereRef.current.rotation.y += rotationSpeed * delta;
      sphereRef.current.rotation.z += rotationSpeed * delta * 0.5;

      // Update material properties for pulse
      if (sphereRef.current.material) {
        sphereRef.current.material.emissiveIntensity = pulse * 0.5;
        sphereRef.current.material.needsUpdate = true;
      }
    }
  });

  return (
    <Canvas style={{ height: '100%', width: '100%' }} camera={{ position: [0, 0, 5] }}>
      {/* Ambient light to make the emissive visible */}
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={0.5} />
      <Sphere
        ref={sphereRef}
        args={[1, 32, 32]}
        material={{
          color: orbColor,
          emissive: orbColor,
          emissiveIntensity: pulse * 0.5,
          roughness: 0.2,
          metalness: 0.8,
          // Add a slight glow effect
          // Note: three.js doesn't have a direct glow, we can use emissive and bloom in postprocessing,
          // but for simplicity we rely on emissive.
        }}
      />
      {/* Optional: add a ring or particles for extra effect */}
      {/* For now, we keep it simple */}
    </Canvas>
  );
};

export default HolographicOrb;