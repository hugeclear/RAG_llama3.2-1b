import React, { useEffect, useState } from 'react';
import { getHealth } from '../services/api';
import { useNavigate } from 'react-router-dom';

const HealthComponent: React.FC = () => {
  const [status, setStatus] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await getHealth();
        setStatus(response.data.status);
      } catch (error) {
        console.error('Error checking health:', error);
      }
    };
    checkHealth();
  }, []);

  return (
    <div>
      <h2>Health Status</h2>
      <p>{status || 'Checking health...'}</p>
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};

export default HealthComponent;