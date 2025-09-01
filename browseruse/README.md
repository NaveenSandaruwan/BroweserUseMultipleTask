# BrowserUse Continuous Control Examples

This directory contains examples of how to use the BrowserUse library for continuous browser control.

## Available Scripts

### 1. keepgoing.py

The main example that demonstrates continuous browser control with persistent sessions.

```bash
# Run in continuous mode (default)
python keepgoing.py

# Run in legacy mode (creates new agent for each task)
python keepgoing.py --legacy

# Run a single task from command line
python keepgoing.py "search for machine learning tutorials"
```

### 2. continuous_browser_example.py

A simpler example that just demonstrates the continuous_browser_control method.

```bash
python continuous_browser_example.py
```

### 3. customprof.py

A minimal example showing continuous browser control with a specific task.

```bash
python customprof.py
```

### 4. browser_manager.py

An alternative approach that creates a new agent for each task but reuses the browser session.
This approach avoids the QueueShutDown errors that can occur with long-running agents.

```bash
python browser_manager.py
```

## How Continuous Browser Control Works

The continuous browser control feature:

1. Keeps the browser session alive between tasks
2. Preserves history and context between interactions
3. Allows for follow-up questions that build on previous context
4. Provides a simple interactive interface

## Implementation Approaches

There are two main approaches demonstrated in this repository:

### Approach 1: Reuse the Same Agent (continuous_browser_control)

The `continuous_browser_control` method on the Agent class:

- Takes an optional initial task to start with
- Runs in an interactive loop asking for follow-up tasks
- Maintains browser state and agent context between tasks
- Handles interruptions gracefully (Ctrl+C to pause/exit)
- Provides both async and sync versions for flexibility

For continuous interaction in your own code, use:

```python
agent = Agent(task="", llm=your_llm, browser_profile=your_profile)
await agent.continuous_browser_control(initial_task="Your initial task")
```

Or for synchronous code:

```python
agent = Agent(task="", llm=your_llm, browser_profile=your_profile)
agent.continuous_browser_control_sync(initial_task="Your initial task")
```

#### Potential Issues

This approach can sometimes encounter QueueShutDown errors due to the event bus being shut down after a task completes. Our implementation tries to handle this by reinitializing the event bus between tasks.

### Approach 2: Create New Agents but Reuse Browser Session (BrowserAgentManager)

An alternative approach that avoids event bus issues by creating a new agent for each task while maintaining the browser session:

- Separates browser session management from agent lifecycle
- Creates fresh agent instance for each task (avoids state issues)
- Shares the same browser session across all agents (preserves browser state)
- More robust against internal errors

For this approach, use the BrowserAgentManager class:

```python
manager = BrowserAgentManager(llm=your_llm)
await manager.run_continuous()
```

## Which Approach to Use?

- If you want to preserve both agent state and browser state, use **Approach 1** (continuous_browser_control)
- If you're encountering QueueShutDown errors or just want a more robust solution, use **Approach 2** (BrowserAgentManager)
- For quick experimentation, both approaches work well
