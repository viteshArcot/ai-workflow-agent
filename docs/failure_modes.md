# Failure Modes: How This Thing Actually Breaks

Agent systems don't just "work or not work" - they fail in weird, subtle ways that took me a while to understand. Here's what I've learned from debugging this thing.

## Priority Classification Failures

**Wrong classifications (happens more than I'd like)**

Real example that caught me off guard: "Schedule urgent meeting with CEO" got classified as "normal." Turns out my training data had lots of "urgent server crash" examples but no "urgent meeting" ones. The model learned that "meeting" = normal priority.

Why this is tricky: The model is technically working correctly based on its training, but it's obviously wrong from a user perspective. This taught me that small training datasets create weird blind spots.

**Domain drift**
I trained the model mostly on tech support queries. When I started testing with marketing or HR requests, accuracy dropped noticeably. "Urgent campaign launch" doesn't match the patterns it learned from "urgent server down."

**Vectorizer weirdness**
Sometimes queries with lots of domain-specific jargon get poor vector representations. The TF-IDF vectorizer just doesn't know what to do with terms it's never seen.

## Task Generation Failures (The Fun Ones)

**Over-generation drives me crazy**

Worst case I've seen: "Fix login bug" turned into 15 micro-tasks including "open your IDE," "check git status," and "take a deep breath." The LLM was trying to be helpful but completely missed the appropriate level of granularity.

This happens when the prompt doesn't give enough context about what level of detail I want. Still tweaking this.

**Under-generation is just as bad**
"Redesign entire user interface" became ["Update UI", "Test changes"]. Technically correct but completely unhelpful. The LLM didn't grasp the complexity of the request.

**JSON parsing failures (my nemesis)**
Despite very explicit instructions, the LLM still returns malformed JSON about 2% of the time. Common patterns:
- Missing closing brackets: `["task 1", "task 2"`
- Extra text: `Here are the tasks: ["task 1", "task 2"]`
- Markdown formatting: `\`\`\`json\n["task 1"]\n\`\`\``

I've gotten pretty good at cleaning these up, but it's still annoying.

**Context hallucination (the sneaky one)**
This one took me a while to notice. The LLM would generate tasks that referenced specific files, APIs, or systems that don't exist. For example, "Update documentation" became "Update the user_guide.md file in the docs folder" - sounds reasonable, but there is no user_guide.md file.

Users would follow these tasks and get confused when the referenced resources didn't exist.

## Cascading Failures (The Scary Ones)

These are the worst because one small error amplifies through the entire pipeline.

**Priority → Generation cascade**
When "server down" gets misclassified as "normal," the task generator creates casual troubleshooting tasks like "check the server when you have time." For a critical outage, this is obviously wrong.

**Generation → Summarization cascade**
When the task generator returns malformed JSON, the summarizer tries to process it and creates a nonsense summary. The user sees something like "Priority: urgent. Tasks include: SyntaxError: invalid JSON."

**Context poisoning**
If I provide bad knowledge context (outdated documentation, wrong system info), it affects both task generation and summarization. Single bad input poisons the entire execution.

## Why Agent Failures Are Different

**Non-deterministic**
Same input can fail differently each time due to LLM variability. Makes debugging much harder than traditional software.

**Plausible but wrong**
Traditional software usually fails obviously (crashes, exceptions). Agent systems often produce outputs that look reasonable but are subtly wrong.

**Context sensitive**
Failures often depend on subtle context that's hard to reproduce. A query that works fine in one domain might fail in another.

**Hard to test**
How do you write unit tests for "generate good tasks"? Traditional testing approaches don't work well.

## What I Do About It

**Lots of fallbacks**
Every LLM call has a fallback response. Every parsing operation has error handling. Better to return something generic than crash.

**Conservative defaults**
When in doubt, choose the safer option. "Normal" priority instead of "urgent." Simple tasks instead of complex ones.

**Comprehensive logging**
I log inputs, outputs, and intermediate states for every execution. Essential for debugging non-deterministic failures.

**Manual quality checks**
I regularly review recent outputs to catch patterns I might have missed. Tedious but necessary.

## What I Still Don't Handle Well

**Semantic correctness**
I can detect JSON parsing failures, but not whether the tasks actually make sense for the query.

**User intent mismatch**
Hard to detect when the system understood the words but missed what the user actually wanted.

**Temporal context**
System doesn't understand time-sensitive aspects. "Fix this before the demo tomorrow" gets the same treatment as "fix this eventually."

**Domain boundaries**
System doesn't know when it's generating tasks outside its knowledge domain. It'll confidently create tasks for things it knows nothing about.

These limitations are why I keep the system constrained and don't claim it can handle everything. Better to be honest about what doesn't work than pretend it's more capable than it is.