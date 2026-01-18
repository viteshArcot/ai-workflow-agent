import React, { useState, useEffect } from 'react';
import MetricsCards from '../components/MetricsCards';
import { getMetrics } from '../api';

const Metrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const response = await getMetrics();
      setMetrics(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch metrics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">System Metrics</h1>
        <p className="text-gray-600">Performance and accuracy insights</p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <MetricsCards metrics={metrics} loading={loading} />
    </div>
  );
};

export default Metrics;