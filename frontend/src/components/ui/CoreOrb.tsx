import React from 'react';

const CoreOrb: React.FC = () => {
  return (
    <div style={{
      width: '120px',
      height: '120px',
      borderRadius: '50%',
      background: 'radial-gradient(circle at center, #00E5FF 0%, #050816 70%)',
      border: '2px solid rgba(0,229,255,0.3)',
      boxShadow: '0 0 20px rgba(0,229,255,0.2)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        background: 'radial-gradient(circle at center, rgba(0,229,255,0.1) 0%, transparent 70%)',
        border: '1px solid rgba(0,229,255,0.2)'
      }}></div>
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        background: '#00E5FF',
        boxShadow: '0 0 15px #00E5FF'
      }}></div>
    </div>
  );
};

export default CoreOrb;