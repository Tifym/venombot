import React, { useEffect, useState } from 'react';

const PositionPanel = () => {
    const [positions, setPositions] = useState([]);

    const fetchPositions = async () => {
        try {
            const res = await fetch('/api/positions');
            const data = await res.json();
            setPositions(data);
        } catch (e) { console.error("Position fetch error:", e); }
    };

    useEffect(() => {
        fetchPositions();
        const interval = setInterval(fetchPositions, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="position-panel" style={{ 
            display: 'flex', gap: '1rem', overflowX: 'auto', 
            background: '#1a1a1a', padding: '1rem', borderTop: '1px solid #333' 
        }}>
            {positions.length === 0 ? (
                <span style={{ color: '#444' }}>NO ACTIVE POSITIONS</span>
            ) : positions.map(p => (
                <div key={p.position_id} style={{
                    background: '#222', padding: '0.5rem 1rem', borderRadius: '4px', borderLeft: `3px solid ${p.direction === 'LONG' ? '#00c853' : '#ff1744'}`,
                    whiteSpace: 'nowrap'
                }}>
                    <span style={{ fontWeight: 'bold' }}>{p.pair}</span> | {p.direction} | Entry: {p.entry_price.toFixed(2)}
                </div>
            ))}
        </div>
    );
};
export default PositionPanel;
