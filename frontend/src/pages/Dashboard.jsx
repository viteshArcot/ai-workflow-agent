import React, { useState } from 'react';
import QueryForm from '../components/QueryForm';
import WorkflowResult from '../components/WorkflowResult';
import { executeWorkflow } from '../api';

const Dashboard = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (query) => {
    setLoading(true);
    setError(null);
    try {
      const response = await executeWorkflow(query);
      setResult(response.data);
      console.log('Success:', response.data);
    } catch (err) {
      console.error('Error details:', err);
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Workflow Agent</h1>
        <p className="text-gray-600">AI-powered task orchestration</p>
      </div>

      <QueryForm onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <WorkflowResult result={result} />
    </div>
  );
};

export default Dashboard;