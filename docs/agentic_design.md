# What "Agentic" Actually Means Here

I spent a lot of time figuring out what makes a system "agentic" vs just "automated." Here's what I learned.

## My Working Definition

When I say this system is "agentic," I don't mean it's fully autonomous or can do whatever it wants. What I mean:

**It exhibits goal-directed behavior:** Given a query, it works toward generating actionable tasks. It's not just following a script - it adapts based on the input.

**It maintains state across steps:** The priority classification affects task generation, which affects summarization. Each step builds on the previous ones.

**It makes contextual decisions:** The LLM adapts its outputs based on priority level and available knowledge context.

**But it's constrained:** It can't change its own workflow, skip steps, or modify system behavior.

This is what I call "constrained agency" - meaningful autonomy within defined boundaries.

## Why I Limited the Autonomy

Initially, I wanted to build something more autonomous. But I quickly realized that would make the project impossible to debug or understand.

**Debugging nightmare:** When something goes wrong with a fully autonomous agent, where do you even start looking? With constrained workflows, I know exactly which node failed.

**Unpredictable resource usage:** If the agent could decide to make extra API calls or use different models, costs would be impossible to predict.

**Failure amplification:** Small errors in autonomous systems can cascade in unpredictable ways. Constraints contain the damage.

**Learning goals:** I wanted to understand workflow orchestration, not build a black box.

## Agent vs Tool vs Workflow

This distinction confused me for a while. Here's how I think about it now:

**Tool systems:** You explicitly call functions. Like `calculator(5+3)` - you decide what to use and when.

**Workflow systems:** Predefined sequence of operations. No decision-making, just execution.

**Agent systems:** The system decides what to do next based on context and goals.

My approach is a hybrid - workflow structure with agentic decision-making at specific nodes. The workflow is fixed, but the content generation is adaptive.

## Where Agency Happens in My System

**Node 1 (Priority Classifier):** Limited agency - makes classification decisions within trained model bounds. It's "smart" but constrained by training data.

**Node 2 (Task Generator):** High agency - creative task breakdown, adapts to priority and context. This is where I want the most flexibility.

**Node 3 (Summarizer):** Medium agency - creative summarization but within format requirements. Acts as a quality gate.

**Node 4 (Logger):** Zero agency - pure deterministic storage. Intentionally "dumb."

The agency is distributed across nodes rather than concentrated in one decision-making component.

## Common Agentic Failures I Avoid

Building this taught me about failure modes specific to agent systems:

**Tool hallucination:** Agent tries to use tools that don't exist or uses them incorrectly. I avoid this by not giving the LLM tool selection capabilities.

**Goal drift:** Agent starts working on a different problem than requested. I prevent this by keeping the original query visible to all nodes.

**Infinite loops:** Agent gets stuck in recursive reasoning. My linear DAG structure makes this impossible.

**Over-optimization:** Agent spends too much time on minor details. Fixed workflow prevents endless refinement loops.

## Why This Approach Works for Learning

This constrained agentic design taught me:

- How to balance AI creativity with system predictability
- Where to allow autonomy vs where to enforce constraints  
- How to debug multi-step AI systems effectively
- What failure modes emerge in agent-like systems

It's not the most sophisticated agent architecture possible, but it's one I can understand, debug, and improve systematically.

## What I'd Change Next Time

If I were building this again, I might experiment with:

**Conditional branching:** Maybe urgent tasks should follow a different path than normal ones?

**Confidence scoring:** The agent could indicate how certain it is about its decisions.

**Self-correction:** Simple retry logic when outputs seem obviously wrong.

But I'd still keep the core constraint: the agent can't modify its own architecture. That boundary seems crucial for maintainability.

## The Meta-Insight

Building this taught me that "agentic" isn't binary - it's a spectrum. The question isn't "is this an agent?" but "where does this system have agency, and where doesn't it?"

Most production AI systems probably fall somewhere in the middle of this spectrum, like mine does. Full autonomy sounds cool in demos, but constrained agency might be more practical for real applications.