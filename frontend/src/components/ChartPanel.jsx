import React, { useEffect, useRef } from 'react';
import { createChart, CrosshairMode } from 'lightweight-charts';

const ChartPanel = ({ pair, timeframe }) => {
  const chartContainerRef = useRef();
  const seriesRef = useRef();

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      layout: { background: { color: '#1a1a1a' }, textColor: '#d1d4dc' },
      grid: { vertLines: { color: '#2b2b2b' }, horzLines: { color: '#2b2b2b' } },
      timeScale: { borderColor: '#2b2b2b', timeVisible: true }
    });
    
    const series = chart.addCandlestickSeries({
      upColor: '#00c853', downColor: '#ff1744', 
      borderVisible: false, wickUpColor: '#00c853', wickDownColor: '#ff1744'
    });
    seriesRef.current = series;

    // Fetch History
    fetch(`/api/klines?pair=${pair}&timeframe=${timeframe}&limit=100`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          const formatted = data.sort((a,b) => a.time - b.time).map(k => ({
            time: new Date(k.time).getTime() / 1000,
            open: k.open, high: k.high, low: k.low, close: k.close
          }));
          series.setData(formatted);
        }
      })
      .catch(err => console.error("History fetch error:", err));

    const handleResize = () => chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [pair, timeframe]);

  return (
    <div style={{ position: 'relative' }}>
      <div ref={chartContainerRef} style={{ width: '100%', height: '400px' }} />
      <div style={{ position: 'absolute', top: '10px', left: '10px', color: '#888', zIndex: 10 }}>
        {pair} | {timeframe}
      </div>
    </div>
  );
};
export default ChartPanel;
