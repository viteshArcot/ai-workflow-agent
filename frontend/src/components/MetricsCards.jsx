import React from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';

const MetricsCards = ({ metrics, loading }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-md p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <p className="text-gray-500">No metrics available</p>
      </div>
    );
  }

  // Mock data for accuracy trend chart
  const trendData = [
    { name: 'Day 1', accuracy: 0.82 },
    { name: 'Day 2', accuracy: 0.85 },
    { name: 'Day 3', accuracy: metrics.classifier_accuracy || 0.87 },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h3 className="text-sm font-medium text-gray-500 mb-2">Total Requests</h3>
          <p className="text-3xl font-bold text-gray-900">{metrics.total_requests || 0}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h3 className="text-sm font-medium text-gray-500 mb-2">Model Accuracy</h3>
          <p className="text-3xl font-bold text-green-600">
            {((metrics.classifier_accuracy || 0) * 100).toFixed(1)}%
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h3 className="text-sm font-medium text-gray-500 mb-2">Avg Latency</h3>
          <p className="text-3xl font-bold text-blue-600">
            {metrics.node_latencies?.task_generator || 'N/A'}
          </p>
        </motion.div>
      </div>

      {/* Node Latencies */}
      {metrics.node_latencies && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-md p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Node Latencies</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(metrics.node_latencies).map(([node, latency]) => (
              <div key={node} className="text-center">
                <p className="text-sm text-gray-500 capitalize">{node.replace('_', ' ')}</p>
                <p className="text-lg font-semibold text-gray-900">{latency}</p>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Accuracy Trend Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-lg shadow-md p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Accuracy Trend</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData}>
              <XAxis dataKey="name" />
              <YAxis domain={[0.8, 1]} />
              <Line 
                type="monotone" 
                dataKey="accuracy" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={{ fill: '#3B82F6' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </div>
  );
};

export default MetricsCards;