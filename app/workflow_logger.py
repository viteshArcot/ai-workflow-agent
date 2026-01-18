from typing import List
from . import database

class DatabaseLogger:
    """Deterministic data persistence with zero AI involvement.
    
    This component intentionally has NO agent capabilities because:
    
    1. DATA INTEGRITY: Database operations must be deterministic and reliable
    2. AUDIT TRAIL: Need consistent, structured records for debugging and analysis
    3. SECURITY: Don't give AI components direct database access
    4. SEPARATION OF CONCERNS: AI decides WHAT to log, deterministic code handles HOW
    5. FAILURE ISOLATION: Database issues shouldn't affect AI decision-making
    
    Why this matters for agent systems:
    - Agents make decisions, but systems handle persistence
    - Mixing AI with critical infrastructure operations creates unpredictable failures
    - Audit trails are essential for debugging multi-step agent behaviors
    - Clear boundaries between "smart" and "reliable" components
    
    This demonstrates a key principle: not everything in an agent system
    needs to be "intelligent" - some components should be boring and reliable.
    """
    
    def log_execution(self, input_text: str, priority: str, tasks: List[str], summary: str) -> int:
        """Persist workflow execution results with error handling.
        
        This is intentionally simple and deterministic:
        - No AI decision-making about what to log
        - No dynamic schema modifications
        - No "smart" data processing or analysis
        - Just reliable, consistent data storage
        
        Failure modes I handle:
        - Database connection issues (graceful degradation)
        - Disk space problems (log error, don't crash workflow)
        - Data validation errors (sanitize inputs)
        
        What I don't handle well yet:
        - Retry logic for transient failures
        - Backup and recovery mechanisms
        - Log rotation and cleanup
        - Performance optimization for large datasets
        """
        try:
            return database.log_request(input_text, priority, tasks, summary)
        except Exception as e:
            # Log the error but don't crash the workflow
            # In production, would use proper logging framework
            print(f"⚠️ Database logging failed: {e}")
            return -1  # Indicate failure but allow workflow to continue
    
    def get_history(self, limit: int = 10):
        """Retrieve execution history for analysis and debugging.
        
        This supports the agent evaluation process by providing:
        - Historical decision patterns
        - Performance trends over time
        - Input/output examples for quality assessment
        - Failure pattern analysis
        """
        try:
            return database.get_history(limit)
        except Exception as e:
            print(f"⚠️ Failed to retrieve history: {e}")
            return []  # Return empty list rather than crashing
    
    def get_count(self) -> int:
        """Get total execution count for basic metrics.
        
        Simple metric that helps track:
        - System usage patterns
        - Performance trends
        - Data growth for capacity planning
        """
        try:
            return database.get_count()
        except Exception as e:
            print(f"⚠️ Failed to get count: {e}")
            return 0  # Return safe default

workflow_logger = DatabaseLogger()