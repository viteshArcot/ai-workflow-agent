# Design Decisions: What I Tried and Why

These are my notes on the key decisions I made while building this. Some worked out better than others.

## ML for Priority Classification

I went back and forth on this one. Initially considered:

**Rule-based approach:**
```python
if "urgent" in query.lower() or "crash" in query.lower():
    return "urgent"
```
This felt too brittle. What about "urgent meeting" vs "urgent server crash"? Context matters.

**LLM classification:**
```python
priority = llm.complete("Classify this as urgent or normal: " + query)
```
Tried this first, actually. But it was inconsistent - same query would sometimes get different priorities. Also added latency to every request.

**Why I settled on DecisionTreeClassifier:**
- Fast and deterministic (no API calls)
- I can actually see the decision path when debugging
- Consistent results (same input = same output)
- Works okay with small datasets
- Easy to retrain when I get new examples

Downside: Probably won't generalize well to domains very different from my training data. But good enough for learning.

## Keeping the LLM Out of Orchestration

This was a conscious choice. The LLM doesn't get to:
- Skip steps it thinks are unnecessary
- Reorder the workflow based on input type
- Decide what gets logged
- Make meta-decisions about its own processing

Why? Because I want predictable system behavior. When something goes wrong, I need to know exactly where to look. If the LLM could modify the workflow, debugging would be a nightmare.

The LLM is good at content generation, not system orchestration. Learned this the hard way after some early experiments with more autonomous approaches.

## SQLite Was the Right Choice (For Now)

Considered:
- **PostgreSQL**: Overkill for this stage, adds deployment complexity
- **Redis**: Good for caching, but I need persistent structured data
- **JSON files**: No querying capabilities, concurrency issues
- **In-memory only**: Lose data on restart

SQLite hits the sweet spot of "just works" for a learning project. Zero configuration, handles concurrent reads/writes fine at this scale, easy to inspect data during development.

Will probably need something more robust if this ever scales up, but that's a future problem.

## What I Rejected and Why

**Single function approach:**
```python
def process_query(query):
    return llm.complete(f"Prioritize and break down: {query}")
```
Too simple. No structure, hard to debug, expensive, inconsistent output format.

**Rule-based everything:**
```python
if "crash" in query or "down" in query:
    priority = "urgent"
    tasks = ["Check logs", "Restart service", "Monitor"]
```
Too brittle. Doesn't handle context, becomes a maintenance nightmare as edge cases accumulate.

**Full agent framework (LangChain, etc.):**
Considered this briefly. Rejected because it would hide the orchestration logic I'm trying to understand. Also adds a lot of complexity for what I'm trying to learn.

**Multi-agent systems:**
Multiple LLMs debating priorities? Sounds cool, but way too complex and expensive for a learning project.

**Recursive workflows:**
Agents that modify their own workflow based on results? Interesting idea, but creates potential for infinite loops and makes debugging nearly impossible.

## Decisions I'm Still Not Sure About

**Linear workflow with no branching:**
Currently everything goes through all 4 steps. Maybe urgent tasks should skip summarization? Or normal tasks could skip detailed logging? Haven't experimented with this yet.

**Temperature settings:**
Using 0.3 for task generation, 0.2 for summarization. These feel reasonable but I haven't systematically tested alternatives.

**Fallback strategies:**
Currently just return generic tasks when LLM fails. Could probably be smarter about this - maybe use the priority to generate more appropriate fallbacks?

**Context integration:**
Right now I just append knowledge context to prompts. There's probably a better way to integrate this information.

## What I'd Change If Starting Over

Probably would start with async processing from the beginning. The synchronous approach works fine for learning, but makes it harder to add features like retry logic or parallel processing later.

Might also invest more time upfront in evaluation frameworks. Currently doing mostly manual quality checks, which doesn't scale well.

Would definitely add more comprehensive logging earlier. Debugging multi-step AI systems requires really good observability.

## The Meta-Decision: Keep It Simple

The biggest decision was to resist the urge to make this more sophisticated. Could have added:
- Memory systems across sessions
- Dynamic model selection
- Complex retry mechanisms
- Multi-modal inputs
- Real-time learning

But I wanted to understand the fundamentals first. Complexity can always be added later, but it's hard to remove once it's there.

This approach worked well for learning. I understand every piece of the system and can explain exactly why each decision was made.