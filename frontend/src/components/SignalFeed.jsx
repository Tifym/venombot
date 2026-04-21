import React, { useEffect, useState } from 'react';

const SignalCard = ({ signal, onApprove, onReject }) => (
  <div className="signal-card" style={{
    background: '#222', borderLeft: `4px solid ${signal.direction === 'LONG' ? '#00c853' : '#ff1744'}`,
    padding: '1rem', borderRadius: '4px', display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.5rem'
  }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold' }}>
      <span>{signal.pair} | {signal.primary_timeframe}</span>
      <span style={{ color: signal.direction === 'LONG' ? '#00c853' : '#ff1744' }}>
        {signal.direction} ({Math.round(signal.score * 100)}%)
      </span>
    </div>
    <div style={{ fontSize: '0.8rem', color: '#aaa', display: 'flex', gap: '1rem' }}>
      <span>Price: {signal.entry_price.toFixed(2)}</span>
      <span>SL: {signal.stop_loss.toFixed(2)}</span>
    </div>
    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
      <button onClick={() => onApprove(signal.signal_id)} style={{ background: '#00c853', color: 'white', border: 'none', padding: '0.4rem 1rem', borderRadius: '4px', cursor: 'pointer' }}>APPROVE</button>
      <button onClick={() => onReject(signal.signal_id)} style={{ background: '#333', color: 'white', border: 'none', padding: '0.4rem 1rem', borderRadius: '4px', cursor: 'pointer' }}>REJECT</button>
    </div>
  </div>
);

const SignalFeed = () => {
  const [signals, setSignals] = useState([]);

  const fetchSignals = async () => {
    try {
      const res = await fetch('/api/signals?status=pending');
      const data = await res.json();
      setSignals(data);
    } catch (e) { console.error("Signal fetch error:", e); }
  };

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (id) => {
    await fetch(`/api/signals/${id}/approve`, { method: 'POST' });
    fetchSignals();
  };

  const handleReject = async (id) => {
    await fetch(`/api/signals/${id}/reject`, { method: 'POST' });
    fetchSignals();
  };

  return (
    <div className="signal-feed" style={{ background: '#111', padding: '1rem', borderRadius: '8px', overflowY: 'auto' }}>
      <h3 style={{ margin: '0 0 1rem 0', fontSize: '0.9rem', color: '#666' }}>SIGNAL FEED</h3>
      {signals.length === 0 ? <div style={{ color: '#444' }}>Waiting for signals...</div> : signals.map(s => (
        <SignalCard key={s.signal_id} signal={s} onApprove={handleApprove} onReject={handleReject} />
      ))}
    </div>
  );
};
export default SignalFeed;
