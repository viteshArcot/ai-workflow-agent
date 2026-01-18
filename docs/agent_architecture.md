# Agent Architecture

## What "Agent" Means Here

This isn't a fully autonomous AI agent that makes its own decisions about everything. Instead, it's a **constrained workflow agent** - I give it structure and decision points, but limit where it can act independently.

The "agent" part comes from:
- It can classify tasks without me telling it exactly how
- It generates contextual responses based on the input
- It maintains state across multiple processing steps
- It logs its own actions for future reference

But I intentionally constrain it by:
- Using a predefined DAG structure (no self-modification)
- Making prioritization decisions with ML, not LLM reasoning
- Keeping the workflow linear and predictable

## Why a DAG Instead of a Single LLM Call

I could have just sent everything to the LLM and asked it to "prioritize, generate tasks, and summarize." But that would be:
- Unpredictable (different structure each time)
- Hard to debug (black box reasoning)
- Expensive (processing everything in one large context)
- Difficult to optimize individual steps

The DAG approach lets me:
- Control the flow explicitly
- Optimize each step independently
- Debug failures at specific nodes
- Add instrumentation and metrics per step

## Node Breakdown

### 1. Task Prioritizer
**What it does:** Classifies input as urgent/normal using a trained DecisionTreeClassifier
**Why it exists:** I want consistent, fast prioritization that doesn't depend on LLM mood or prompt engineering
**Autonomy level:** Medium - it makes the decision, but within a trained model's constraints

### 2. Task Generator  
**What it does:** Uses LLM to break down the query into actionable tasks
**Why it exists:** This is where I actually want creative, contextual thinking
**Autonomy level:** High - but constrained by the prompt structure and knowledge context

### 3. Summarizer
**What it does:** Takes the generated tasks and creates a clean summary
**Why it exists:** Separate step ensures consistent output format, regardless of how verbose the generator was
**Autonomy level:** Medium - creative summarization within format constraints

### 4. Logger
**What it does:** Persists everything to SQLite
**Why it exists:** Simple persistence without giving the LLM database access
**Autonomy level:** None - pure deterministic storage

## Where Autonomy is Allowed vs Restricted

**Allowed autonomy:**
- Task content generation (node 2)
- Summary phrasing (node 3)
- Priority classification within trained bounds (node 1)

**Restricted autonomy:**
- Workflow order (always 1→2→3→4)
- Database operations (no LLM access)
- Node skipping or modification
- Self-reflection or meta-reasoning

This gives me the benefits of AI creativity while maintaining system predictability.