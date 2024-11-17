import React, { useEffect, useState } from 'react';
import { getStats } from '../services/api';
import { useNavigate } from 'react-router-dom';

const StatsComponent: React.FC = () => {
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getStats();
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };
    fetchStats();
  }, []);

  return (
    <div>
      <h2>System Stats</h2>
      {stats ? (
        <pre>{JSON.stringify(stats, null, 2)}</pre>
      ) : (
        <p>Loading stats...</p>
      )}
      <button onClick={() => navigate('/')}>Go Home</button>
    </div>
  );
};

export default StatsComponent;