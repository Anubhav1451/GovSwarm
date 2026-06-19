import React from 'react';

const SwarmGraph: React.FC = () => {
  return (
    <div style={{ background: '#0F172A', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '16px', padding: '16px', minHeight: '300px' }}>
      <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '12px' }}>// INTEL AGENT SWARM VISUALIZATION</div>
      <div style={{
        width: '100%',
        height: '200px',
        background: 'radial-gradient(circle at center, rgba(0,229,255,0.05) 0%, transparent 70%)',
        border: '1px solid rgba(0,229,255,0.2)',
        borderRadius: '12px',
        position: 'relative'
      }}>
        {/* Dots representing nodes */}
        <div style={{
          position: 'absolute',
          top: '20%',
          left: '20%',
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: '#00E5FF',
          boxShadow: '0 0 8px #00E5FF'
        }}></div>
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '70%',
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: '#EF4444',
          boxShadow: '0 0 6px #EF4444'
        }}></div>
        <div style={{
          position: 'absolute',
          top: '80%',
          left: '30%',
          width: '10px',
          height: '10px',
          borderRadius: '50%',
          background: '#22C55E',
          boxShadow: '0 0 10px #22C55E'
        }}></div>
        <div style={{
          position: 'absolute',
          top: '40%',
          left: '10%',
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: '#F59E0B',
          boxShadow: '0 0 6px #F59E0B'
        }}></div>
      </div>
    </div>
  );
};

export default SwarmGraph;