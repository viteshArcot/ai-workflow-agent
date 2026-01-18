import pytest
import asyncio
from app.prioritizer import prioritizer
from app.graph import workflow_dag, WorkflowState
from app import database

class TestWorkflowAgent:
    
    def test_classifier_predicts_urgent_correctly(self):
        """Test that classifier correctly identifies urgent queries"""
        # Train the model first
        if not prioritizer.load():
            prioritizer.train()
        
        urgent_query = "Critical server crash needs immediate fix"
        prediction = prioritizer.predict(urgent_query)
        
        assert prediction == "urgent", f"Expected 'urgent' but got '{prediction}'"
    
    def test_logger_writes_to_database(self):
        """Test that logger successfully writes to database"""
        initial_count = database.get_count()
        
        # Log a test execution
        database.log_request(
            input_text="Test query",
            priority="normal", 
            tasks=["Task 1", "Task 2"],
            summary="Test summary"
        )
        
        final_count = database.get_count()
        assert final_count == initial_count + 1, "Database count should increase by 1"
        
        # Verify the logged data
        history = database.get_history(limit=1)
        assert len(history) > 0, "Should have at least one history record"
        assert history[0]["input_text"] == "Test query"
        assert history[0]["priority"] == "normal"
    
    @pytest.mark.asyncio
    async def test_workflow_executes_all_nodes(self):
        """Test that workflow executes all 4 nodes in sequence"""
        # Initialize state
        state = WorkflowState()
        state.query = "Fix production bug"
        
        # Execute workflow
        result = await workflow_dag.execute(state)
        
        # Verify all nodes executed
        expected_nodes = ["Task Prioritizer", "Task Generator", "Summarizer", "Logger"]
        executed_nodes = [step["node"] for step in result.steps]
        
        assert len(executed_nodes) == 4, f"Expected 4 nodes, got {len(executed_nodes)}"
        
        for expected_node in expected_nodes:
            assert expected_node in executed_nodes, f"Node '{expected_node}' not executed"
        
        # Verify state was populated
        assert result.priority in ["urgent", "normal"], "Priority should be set"
        assert len(result.tasks) > 0, "Tasks should be generated"
        assert result.summary != "", "Summary should be generated"
        assert len(result.metrics) > 0, "Metrics should be recorded"

if __name__ == "__main__":
    pytest.main([__file__])