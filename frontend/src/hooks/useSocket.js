import { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';
const SOCKET_URL = '/';
export const useSocket = (pair) => {
  const [states, setStates] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef(null);
  useEffect(() => {
    const socket = io(SOCKET_URL);
    socketRef.current = socket;
    socket.on('connect', () => { setIsConnected(true); if (pair) socket.emit('subscribe_pair', { pair }); });
    socket.on('disconnect', () => setIsConnected(false));
    socket.on('state_update', (data) => {
      if (data.pair === pair) setStates(prev => ({ ...prev, [data.timeframe]: { alfa: data.alfa, beta: data.beta, delta: data.delta, gamma: data.gamma } }));
    });
    return () => socket.disconnect();
  }, [pair]);
  return { states, isConnected };
};
