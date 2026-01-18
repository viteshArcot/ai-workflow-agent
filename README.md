# AI Workflow Agent

A learning project where I explored constrained workflow orchestration with AI components. Built this to understand agentic AI concepts without the hype.

## What I Was Trying to Learn

This isn't a production AI platform. It's my attempt to understand:

- How to build predictable workflows that include AI decision-making
- When to use ML vs LLM vs deterministic logic for different steps
- How to constrain AI autonomy while preserving useful creativity
- Practical trade-offs in workflow orchestration design

Basically, I wanted to understand the fundamentals before jumping into complex agent frameworks.

## What I Intentionally Avoided

- Full AI autonomy (the system can't modify its own workflow)
- Complex multi-agent interactions  
- Enterprise-scale features like distributed processing
- Marketing buzzwords about "AI-powered platforms"

I kept it simple on purpose. Complexity can always be added later.

## How the Agent Actually Works

This system exhibits what I call **constrained agency** - it makes contextual decisions and maintains state across multiple steps, but within explicit boundaries:

**Where it has autonomy:**
- Task content generation (creative, contextual reasoning)
- Priority classification (within trained model bounds)
- Summary formatting (style and emphasis choices)

**Where it doesn't:**
- Workflow structure (always follows the same 4-step path)
- Tool selection (each node has a fixed function)
- Database operations (deterministic persistence only)
- Meta-reasoning (can't modify its own behavior)

**Why these boundaries exist:**
- **Debuggability:** When something goes wrong, I know exactly which node failed
- **Predictability:** Same input type always follows the same execution path
- **Cost control:** Agent can't decide to make extra API calls or use expensive models
- **Failure isolation:** Errors in one node don't cascade unpredictably

## Why I Chose a Workflow Agent

I considered several approaches and settled on a DAG-based workflow because:

**vs Single LLM Call:**
- More debuggable (can trace failures to specific nodes)
- Better separation of concerns (classification vs generation vs formatting)
- Independent optimization (can improve each step separately)
- Predictable resource usage

**vs Full Agent Autonomy:**
- Easier to understand and debug
- Consistent performance characteristics
- Bounded failure modes
- Better for learning the fundamentals

**vs Rule-Based System:**
- Handles contextual nuance (LLM creativity where needed)
- Adapts to different domains and request types
- Learns from examples (ML classification)
- More flexible than rigid if/then logic

## Architecture

```
Query → [ML Classifier] → [LLM Generator] → [LLM Summarizer] → [Database Logger]
```

**4 nodes, always executed in this order:**

1. **Priority Classifier** - DecisionTreeClassifier (not LLM) for consistent results
2. **Task Generator** - LLM with knowledge context for creative task breakdown  
3. **Summarizer** - LLM for clean output formatting
4. **Logger** - Deterministic database storage (no AI involvement)

I chose this specific structure after trying several alternatives. The linear flow makes debugging much easier.

## Where This Agent Breaks (The Honest Part)

Agent systems fail in subtle ways that are different from traditional software. Here's what I've observed:

**Classification Errors:**
- "Schedule urgent meeting with CEO" might get classified as "normal"
- Model trained on tech queries struggles with other domains
- Small training dataset limits generalization

**Task Generation Failures:**
- Over-generation: "Fix login bug" → 15 micro-tasks
- Under-generation: "Redesign UI" → vague, non-actionable tasks
- Context hallucination: Inventing details not in the original query

**Cascading Failures:**
- Wrong priority classification affects task generation quality
- Bad task generation creates unsummarizable content
- Single bad input can affect entire execution pipeline

**What I Don't Handle Well:**
- Semantic correctness (tasks might be syntactically valid but nonsensical)
- Domain expertise (system doesn't know its knowledge boundaries)
- Temporal context (time-sensitive aspects of requests)
- User intent mismatch (understanding query but missing real goal)

These limitations are why I keep the system constrained and don't claim it can handle everything.

## Tech Stack

**Backend:** FastAPI, scikit-learn, OpenRouter API, SQLite  
**Frontend:** React, TailwindCSS, Vite  
**Testing:** Pytest with async support

Chose these for simplicity and "just works" factor, not because they're the most sophisticated options.

## Documentation

- [Agentic Design](docs/agentic_design.md) - What "agentic" means in this system
- [Workflow Decisions](docs/workflow_decisions.md) - Why each node exists and alternatives considered
- [Failure Modes](docs/failure_modes.md) - How and why the agent fails
- [Evaluation Strategy](docs/evaluation_strategy.md) - How success is measured without ground truth
- [Interview Prep Notes](docs/interview_talking_points.md) - What I learned building this
- [Agent Architecture](docs/agent_architecture.md) - System structure and constraints
- [Design Decisions](docs/design_decisions.md) - Technical choices and trade-offs
- [Limitations](docs/limitations_and_future.md) - What this doesn't handle

## Running the System

**Backend:**
```bash
cd /workspaces/ai-workflow-agent
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd /workspaces/ai-workflow-agent/frontend
npm run dev
```

Access at `http://localhost:3000`

## Sample Queries That Work

**Urgent (ML classifier usually gets these right):**
- "Critical server crash needs immediate fix"
- "Database connection failing for all users"

**Normal:**
- "Update user documentation for new features"
- "Schedule team meeting for next week"

The system works best with clear, actionable requests. Vague or highly domain-specific queries often produce mediocre results.

## What I'd Improve If I Had More Time

**Evaluation Framework:**
- More systematic quality measurement approaches
- Automated consistency testing across similar inputs
- Better error pattern detection and analysis

**Error Recovery:**
- Retry logic for transient failures
- Self-correction mechanisms when outputs seem obviously wrong
- More sophisticated fallback strategies

**Performance:**
- Async processing for better scalability
- Caching for repeated similar queries
- Database optimization for larger datasets

**Agent Capabilities:**
- Confidence scoring for uncertain decisions
- Domain-specific knowledge integration
- Better handling of temporal and contextual nuance

## What I Actually Learned

- **Workflow orchestration is harder than AI components:** Most bugs were in state management and error handling, not LLM calls
- **Constraints enable reliability:** Limiting agent autonomy made it more useful and debuggable
- **Agent evaluation is fundamentally different:** No ground truth labels, need qualitative assessment
- **Failure modes amplify in multi-step systems:** Small errors cascade through the pipeline
- **Simple approaches often work better:** Complex agent architectures become very hard to debug

The biggest insight: agent systems are more about engineering discipline than AI sophistication. The hard parts aren't the ML models - they're the orchestration, error handling, and evaluation.

This project taught me to think about AI systems as components in larger workflows, with explicit boundaries between creative AI and deterministic system operations.