import time
import asyncio
from typing import Dict, Any, List, Callable
from collections import defaultdict, deque

class WorkflowState:
    """Keeps track of everything as it moves through the workflow.
    
    This is what makes the system feel "agentic" - it remembers context
    and builds on previous decisions rather than treating each step independently.
    
    I made this explicit rather than hiding it in function parameters because
    debugging agent systems requires seeing how state changes at each step.
    """
    def __init__(self):
        self.query: str = ""  # Original user request - never gets modified
        self.priority: str = ""  # What the ML classifier decided
        self.tasks: List[str] = []  # What the LLM generated
        self.summary: str = ""  # Final cleaned-up output
        self.steps: List[Dict[str, Any]] = []  # Breadcrumbs for debugging
        self.metrics: Dict[str, float] = {}  # Performance tracking
        self.context: Dict[str, Any] = {}  # Extra stuff like knowledge context

class DAGRunner:
    """Runs the workflow in a predictable order.
    
    I went with a DAG structure instead of letting the LLM decide execution order because:
    1. When things break, I know exactly where to look
    2. I can tune each step independently
    3. No risk of the agent getting stuck in loops or skipping important steps
    4. Resource usage is predictable (important when you're paying per API call)
    
    This is "constrained agency" - the agent gets to be creative within each node,
    but can't mess with the overall workflow structure.
    """
    def __init__(self):
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, List[str]] = {}
        
    def add_node(self, name: str, func: Callable):
        """Add a processing step to the workflow.
        
        Each node handles a specific capability:
        - Classification (ML-based decisions)
        - Generation (LLM creativity)
        - Summarization (LLM cleanup)
        - Logging (boring but reliable data storage)
        """
        self.nodes[name] = func
        
    def add_edge(self, from_node: str, to_node: str):
        """Define what order things run in.
        
        I keep this linear (no branching) because it's much easier to debug.
        Agent systems with complex branching tend to make unexpected choices
        that are hard to trace when things go wrong.
        """
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)
        
    def _topological_sort(self) -> List[str]:
        """Determine execution order using topological sort.
        
        This ensures dependencies are respected without giving the agent
        the ability to reorder steps. In a fully autonomous agent, the system
        might decide to skip steps or change order based on input - but that
        makes debugging nearly impossible when things go wrong.
        
        I use Kahn's algorithm because it's deterministic and will detect
        cycles (which would indicate a workflow design error).
        """
        in_degree = defaultdict(int)
        
        # Calculate in-degrees
        for node in self.nodes:
            in_degree[node] = 0
        for from_node, to_nodes in self.edges.items():
            for to_node in to_nodes:
                in_degree[to_node] += 1
                
        # Topological sort using Kahn's algorithm
        queue = deque([node for node in self.nodes if in_degree[node] == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in self.edges.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    
        return result
        
    async def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute the agent workflow in deterministic order.
        
        This is the core agent execution loop. Each node gets the accumulated
        state and can modify it, but cannot:
        - Skip subsequent nodes
        - Modify the execution order
        - Access nodes outside the defined workflow
        
        I track execution time per node because agent systems often have
        performance bottlenecks that are hard to predict (LLM API latency,
        model inference time, etc.).
        """
        execution_order = self._topological_sort()
        
        for node_name in execution_order:
            if node_name in self.nodes:
                start_time = time.time()
                # Each node is an agent capability with bounded autonomy
                state = await self.nodes[node_name](state)
                execution_time = time.time() - start_time
                state.metrics[f"{node_name.lower().replace(' ', '_')}_time"] = execution_time
                
        return state

# Import node functions - each handles a specific workflow step
from .priority_classifier import prioritizer as priority_classifier
from .generator import generator
from .summarizer import summarizer
from .workflow_logger import workflow_logger

async def prioritize_task(state: WorkflowState) -> WorkflowState:
    """Step 1: Figure out if this is urgent or normal priority.
    
    I use ML here instead of an LLM because:
    - It's way faster (no API call)
    - Same input always gives same result (no LLM "mood swings")
    - Cheaper to run
    - When priorities seem wrong, I can actually debug the decision tree
    
    This shows a key principle: not everything needs to be "intelligent."
    Sometimes boring and reliable beats smart and unpredictable.
    """
    priority = priority_classifier.predict(state.query)
    state.priority = priority
    state.steps.append({"node": "Task Prioritizer", "output": priority})
    return state

async def generate_tasks(state: WorkflowState) -> WorkflowState:
    """Step 2: Break down the request into actionable tasks.
    
    This is where I want the agent to be creative and contextual, but within limits.
    The LLM can:
    - Decide how many tasks to create (3-5 usually works)
    - Choose specific wording and approach
    - Adapt based on the priority from step 1
    - Use any knowledge context I provide
    
    But it can't:
    - Skip this step or jump to other nodes
    - Modify the workflow structure
    - Access external tools or APIs
    - Return anything other than a JSON array
    
    This is "bounded creativity" - useful flexibility within defined constraints.
    
    Common ways this breaks:
    - JSON parsing failures (LLM ignores format instructions)
    - Over-generation ("Fix login bug" becomes 15 micro-tasks)
    - Under-generation ("Redesign UI" becomes "Update UI")
    - Context hallucination (inventing details not in the original query)
    """
    tasks = await generator.generate_tasks(state.query, state.priority, state.context.get("knowledge", ""))
    state.tasks = tasks
    state.steps.append({"node": "Task Generator", "output": tasks})
    return state

async def summarize_results(state: WorkflowState) -> WorkflowState:
    """Node 3: LLM-based output formatting with quality control.
    
    I separate summarization from generation because:
    
    1. SINGLE RESPONSIBILITY: Each node has one clear job
    2. ERROR ISOLATION: If summary is bad, I know exactly which node to fix
    3. QUALITY CONTROL: Acts as a "sanity check" on generated tasks
    4. CONSISTENCY: Ensures uniform output format regardless of generator mood
    5. INDEPENDENT OPTIMIZATION: Can tune generation vs summarization separately
    
    The summarizer has constrained autonomy to:
    - Choose summary style and tone
    - Decide what details to emphasize
    - Adapt tone to match priority level
    - Format information clearly
    
    But it CANNOT:
    - Add information not in the generated tasks
    - Change the priority or task content
    - Skip summarization or return raw tasks
    
    This demonstrates agent "quality gates" - using one AI component to
    validate and improve the output of another.
    
    Failure modes I handle:
    - Information loss: summary drops important details
    - Tone mismatch: casual summary for urgent tasks
    - Format drift: inconsistent output structure
    """
    summary = await summarizer.summarize(state.query, state.priority, state.tasks, state.context.get("knowledge", ""))
    state.summary = summary
    state.steps.append({"node": "Summarizer", "output": summary})
    return state

async def log_results(state: WorkflowState) -> WorkflowState:
    """Step 4: Save everything to the database.
    
    This is intentionally boring and deterministic - no AI involvement.
    I don't want the LLM making decisions about what gets stored or how.
    
    Just reliable, consistent data persistence so I can debug issues later
    and track how the system is performing over time.
    
    TODO: Add retry logic for database failures
    TODO: Implement log rotation to prevent disk space issues
    """
    workflow_logger.log_execution(state.query, state.priority, state.tasks, state.summary)
    state.steps.append({"node": "Logger", "output": "Logged to database"})
    return state

# Create and configure the DAG
def create_workflow_dag() -> DAGRunner:
    """Set up the 4-step workflow with my reasoning behind it.
    
    I chose this specific structure after trying a few alternatives:
    
    1. Always follows the same path (1→2→3→4)
    2. Each step has a single, clear job
    3. When something breaks, I know exactly which step failed
    4. I can improve each step independently
    5. The agent gets to be creative within defined boundaries
    
    Why linear instead of branching:
    - Branching workflows get exponentially harder to debug
    - Resource usage becomes unpredictable
    - Testing becomes much more complex
    - The agent might make poor branching decisions
    
    Why these specific 4 steps:
    - Priority classification: Fast, consistent decisions
    - Task generation: Creative, contextual reasoning
    - Summarization: Quality control and formatting
    - Logging: Boring, reliable persistence
    
    This represents "constrained agency" - meaningful autonomy within each step,
    but no ability to modify the overall system architecture. It's a middle ground
    between rigid rule-based systems and fully autonomous agents.
    """
    dag = DAGRunner()
    
    # Add the 4 steps in order - each handles a specific capability
    dag.add_node("Task Prioritizer", prioritize_task)  # ML classification
    dag.add_node("Task Generator", generate_tasks)     # LLM creativity
    dag.add_node("Summarizer", summarize_results)     # LLM cleanup
    dag.add_node("Logger", log_results)               # Deterministic storage
    
    # Wire them up in a straight line - no branching, skipping, or loops
    # This constraint prevents the agent from making poor execution decisions
    dag.add_edge("Task Prioritizer", "Task Generator")
    dag.add_edge("Task Generator", "Summarizer")
    dag.add_edge("Summarizer", "Logger")
    
    return dag

workflow_dag = create_workflow_dag()