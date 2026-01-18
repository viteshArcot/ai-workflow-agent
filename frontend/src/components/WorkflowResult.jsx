import React, { useState } from 'react';
import { motion } from 'framer-motion';

const WorkflowResult = ({ result }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!result) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-md p-6 mt-6"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Workflow Result</h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-blue-600 hover:text-blue-800"
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {isExpanded && (
        <div className="space-y-4">
          {/* Final Summary */}
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <h4 className="font-medium text-green-800 mb-2">Final Summary</h4>
            <p className="text-green-700">{result.summary}</p>
          </div>

          {/* Priority */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600">Priority:</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              result.priority === 'urgent' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-blue-100 text-blue-800'
            }`}>
              {result.priority}
            </span>
          </div>

          {/* Workflow Steps */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Workflow Steps</h4>
            <div className="space-y-3">
              {result.workflow_steps && result.workflow_steps.map((step, index) => (
                <div key={index} className="border-l-4 border-blue-200 pl-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h5 className="font-medium text-gray-800">{step.node}</h5>
                      <p className="text-sm text-gray-600 mt-1">{step.output}</p>
                    </div>
                    {step.latency && (
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        {step.latency}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Execution Time */}
          {result.execution_time && (
            <div className="text-sm text-gray-500">
              Executed at: {new Date(result.execution_time).toLocaleString()}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default WorkflowResult;