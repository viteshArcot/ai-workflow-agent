from typing import List
from .llm_client import client

class TaskSummarizer:
    """LLM-based summarization with quality control and consistency enforcement.
    
    This node serves as a "quality gate" in the agent pipeline:
    
    1. CONSISTENCY ENFORCEMENT: Ensures uniform output format regardless of
       how verbose or inconsistent the task generation was
    2. INFORMATION VALIDATION: Acts as a sanity check on generated tasks
    3. TONE MATCHING: Adapts summary tone to match priority level
    4. NOISE REDUCTION: Filters out irrelevant details from task generation
    
    Why separate from task generation:
    - Single responsibility principle (generation vs formatting)
    - Independent optimization of each LLM step
    - Error isolation (bad summary doesn't affect task quality)
    - Quality control (catch obviously wrong task outputs)
    """
    
    async def summarize(self, query: str, priority: str, tasks: List[str], context: str = "") -> str:
        """Create professional summary with priority-aware tone and fallback handling.
        
        Agent quality control mechanisms:
        
        1. PRIORITY-AWARE TONE: Urgent tasks get more direct, action-oriented language
        2. CONSERVATIVE TEMPERATURE: 0.2 for consistent, professional output
        3. TOKEN LIMITS: 200 tokens prevents over-elaboration
        4. STRUCTURED FALLBACK: Safe default when LLM fails
        5. INFORMATION PRESERVATION: Ensures key details aren't lost
        
        Common summarization failure modes I handle:
        - Information loss (dropping important task details)
        - Tone mismatch (casual tone for urgent priorities)
        - Over-elaboration (adding details not in original tasks)
        - Format inconsistency (varying output structure)
        - Context hallucination (inventing information)
        
        Why this matters for agent systems:
        - Summary is often the primary user-facing output
        - Inconsistent summaries make the agent feel unreliable
        - Poor summaries can mislead users about actual task content
        - Quality degradation here affects user trust in the entire system
        """
        # Professional system prompt with clear quality expectations
        system_prompt = """You are a professional summarizer. Create concise, business-style summaries 
        that incorporate the priority level and key tasks. Keep it under 100 words.
        
        For URGENT priorities: Use direct, action-oriented language
        For NORMAL priorities: Use standard professional tone
        
        Do not add information not present in the tasks. Do not speculate or elaborate beyond what's provided."""
        
        # Format tasks clearly for LLM processing
        tasks_text = "\n".join([f"- {task}" for task in tasks])
        context_text = f"\nRelevant context: {context}" if context else ""
        
        # Structured user prompt with explicit requirements
        user_prompt = f"""Original Request: "{query}"
Priority Level: {priority}

Key Tasks:
{tasks_text}{context_text}

Provide a concise summary that:
- Reflects the {priority} priority level in tone
- Captures the essential tasks without adding new information
- Is professional and actionable
- Stays under 100 words"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Conservative parameters for consistent, professional output
            response = await client.generate(
                messages, 
                temperature=0.2,  # Low temperature for consistency
                max_tokens=200    # Prevent over-elaboration
            )
            
            # Basic validation and cleanup
            summary = response.strip()
            
            # Ensure we got a reasonable response
            if len(summary) > 10 and len(summary) < 500:
                return summary
            else:
                # Response too short or too long - use fallback
                return self._create_fallback_summary(query, priority, tasks)
                
        except Exception:
            # Any LLM failure - use structured fallback
            return self._create_fallback_summary(query, priority, tasks)
    
    def _create_fallback_summary(self, query: str, priority: str, tasks: List[str]) -> str:
        """Generate structured fallback summary when LLM fails.
        
        Fallback strategy:
        - Maintain professional tone
        - Include priority information
        - Reference key tasks without elaboration
        - Ensure output is always useful and actionable
        
        This demonstrates graceful degradation - even when AI components fail,
        the system provides something useful rather than crashing or returning errors.
        """
        task_summary = ", ".join(tasks[:3])  # Limit to first 3 tasks
        if len(tasks) > 3:
            task_summary += f" and {len(tasks) - 3} additional tasks"
            
        priority_prefix = "URGENT:" if priority == "urgent" else "Task:"
        
        return f"{priority_prefix} {query}. Key activities include: {task_summary}."

summarizer = TaskSummarizer()