import json
from typing import List
from .llm_client import client

class TaskGenerator:
    """LLM-based task generation with guardrails to prevent common failures.
    
    Key principles I learned:
    - Force structured outputs (JSON) to prevent hallucination
    - Explicit boundaries prevent tool misuse
    - Good fallbacks are essential when LLMs inevitably fail
    
    This works pretty well, though I'm still tweaking the prompt to get
    better task granularity. Sometimes it generates too many micro-tasks,
    sometimes too few high-level ones.
    """
    
    async def generate_tasks(self, query: str, priority: str, context: str = "") -> List[str]:
        """Generate task breakdown with fallbacks for when the LLM misbehaves.
        
        Control mechanisms that usually work:
        1. Structured prompts with clear examples
        2. JSON output format (though LLMs still mess this up sometimes)
        3. Low temperature for consistency
        4. Token limits to prevent over-generation
        5. Fallback tasks when parsing fails
        
        Common failure modes I've seen:
        - JSON parsing errors (LLM adds extra text or malformed brackets)
        - Over-generation ("Fix login bug" becomes 15 micro-tasks)
        - Under-generation ("Redesign UI" becomes "Update UI")
        - Context hallucination (inventing file names or details)
        
        The fallback strategy is pretty basic but works for now.
        """
        # System prompt - trying to be very explicit about format requirements
        system_prompt = """You are a task breakdown expert. Break down user requests into specific, actionable subtasks. 
        Return ONLY a valid JSON array of strings. Each task should be clear and actionable.
        
        CRITICAL: Your output must be valid JSON. Do not include explanations, markdown, or other text."""
        
        context_text = f"\nRelevant context: {context}" if context else ""
        
        # User prompt with explicit constraints and examples
        user_prompt = f"""Request: "{query}"
Priority: {priority}{context_text}

Break this down into 3-5 specific subtasks. Return only a JSON array like:
["task 1", "task 2", "task 3"]

Each task should be:
- Specific and actionable
- Appropriate for the {priority} priority level
- Completable by a single person
- Clear about what needs to be done"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Conservative parameters - still experimenting with these
            response = await client.generate(
                messages, 
                temperature=0.3,  # Low enough for consistency, high enough for creativity
                max_tokens=300    # Prevent over-generation
            )
            
            # Aggressive JSON cleaning - LLMs love to add markdown formatting
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            tasks = json.loads(response)
            
            # Basic validation - could be more sophisticated
            if isinstance(tasks, list) and all(isinstance(task, str) for task in tasks):
                if 2 <= len(tasks) <= 7:  # Allow some flexibility
                    return tasks
                else:
                    return self._create_fallback_tasks(query)
            else:
                return self._create_fallback_tasks(query)
                
        except json.JSONDecodeError:
            # Happens more often than I'd like
            return self._create_fallback_tasks(query)
        except Exception:
            # API errors, timeouts, etc.
            return self._create_fallback_tasks(query)
    
    def _create_fallback_tasks(self, query: str) -> List[str]:
        """Generic fallback when the LLM fails - good enough for now.
        
        This is pretty basic but ensures the system always returns something useful.
        Could probably make this smarter by using the priority or query type.
        """
        return [
            f"Analyze requirements for: {query}",
            f"Plan implementation approach", 
            f"Execute the planned solution",
            f"Review and validate results"
        ]

generator = TaskGenerator()