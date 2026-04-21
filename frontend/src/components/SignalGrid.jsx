import React from 'react';

const Box = ({ label, state }) => (
  <div className={`box ${state || 'NEUTRAL'}`} title={label}>
    {label}
  </div>
);

const Row = ({ label, timeframes, states, stateKey }) => (
  <div className="row">
    <div className="row-label">{label}</div>
    <div className="boxes">
      {timeframes.map(tf => (
        <Box 
          key={tf} 
          label={tf} 
          state={states[tf] ? states[tf][stateKey] : 'NEUTRAL'} 
        />
      ))}
    </div>
  </div>
);

const SignalGrid = ({ states }) => {
  const alfas = ['1D', '4H', '3H', '2H', '1H', '24m', '12m', '6m', '3m', '1m'];
  const others = ['1H', '24m', '12m', '6m', '3m', '1m'];

  return (
    <div className="signal-grid" style={{
      display: 'flex', flexDirection: 'column', gap: '0.8rem', 
      background: '#1a1a1a', padding: '1.5rem', borderRadius: '8px', border: '1px solid #333'
    }}>
      <Row label="ALFA" timeframes={alfas} states={states} stateKey="alfa" />
      <Row label="BETA" timeframes={others} states={states} stateKey="beta" />
      <Row label="DELTA" timeframes={others} states={states} stateKey="delta" />
      <Row label="GAMMA" timeframes={others} states={states} stateKey="gamma" />
    </div>
  );
};
export default SignalGrid;
