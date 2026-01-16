# Auto-DataScientist Core Library

Shared core library for the Auto-DataScientist system. Provides state models, logging utilities, and common helpers used across all microservices.

## Installation

```bash
# From the monorepo root
poetry install

# Or install as a local package
cd libs/core
poetry install
```

## Components

### State Models (`core.state`)

LangGraph state definitions for workflow orchestration:

```python
from core import AgentState, DatasetInfo, CodeContext, ApprovalStatus

# Example: Initialize dataset info
dataset = DatasetInfo(
    url="https://example.com/data.csv",
    file_path="/data/dataset.csv",
    is_public=True,
    description="Customer churn dataset"
)

# Example: Create initial state
state: AgentState = {
    "messages": [],
    "user_goal": "Build a classification model",
    "dataset_info": dataset,
    "research_plan": [],
    "code_context": CodeContext(),
    "review_feedback": [],
    "human_approval": ApprovalStatus.PENDING,
    "next_step": "research_agent"
}
```

**State Keys:**
- `messages`: Conversation history with automatic message aggregation
- `user_goal`: Original user prompt
- `dataset_info`: Dataset metadata and location
- `research_plan`: Research steps from Research Agent
- `code_context`: Generated code (EDA + model training)
- `review_feedback`: Feedback from Critic Agent
- `human_approval`: Manual review status (PENDING/APPROVED/REJECTED)
- `next_step`: Next agent to execute

### Logger (`core.logger`)

Industry-grade JSON structured logging:

```python
from core import setup_logger, ContextLogger

# Basic usage
logger = setup_logger("my-service", level="INFO")
logger.info("Service started")

# With context (adds fields to all logs)
ctx_logger = ContextLogger(
    logger,
    service="orchestrator",
    version="0.1.0",
    environment="production"
)
ctx_logger.info("Processing request", request_id="abc-123", user_id="user-1")

# Output (JSON formatted):
# {
#   "timestamp": "2026-01-14T04:49:16Z",
#   "level": "INFO",
#   "logger": "my-service",
#   "message": "Processing request",
#   "module": "main",
#   "function": "handle_request",
#   "line": 42,
#   "service": "orchestrator",
#   "version": "0.1.0",
#   "environment": "production",
#   "request_id": "abc-123",
#   "user_id": "user-1"
# }
```

**Features:**
- JSON structured output for log aggregation
- Contextual logging with custom fields
- Exception tracking
- Compatible with ELK Stack, CloudWatch, Datadog

## Usage in Services

### Orchestrator Service

```python
from core import AgentState, setup_logger

logger = setup_logger("orchestrator")

def process_workflow(state: AgentState):
    logger.info("Starting workflow", user_goal=state["user_goal"])
    # ... workflow logic
```

### Browser Agent Service

```python
from core import setup_logger, CodeContext

logger = setup_logger("browser_agent")

def execute_code(code_ctx: CodeContext):
    logger.info("Executing code in Colab", file_name=code_ctx.file_name)
    # ... browser automation
```

### ML Worker Service

```python
from core import setup_logger, DatasetInfo

logger = setup_logger("ml_worker")

def train_model(dataset: DatasetInfo):
    logger.info("Training model", dataset_path=dataset.file_path)
    # ... model training
```

## Development

```bash
# Install dependencies
poetry install

# Run type checking
poetry run mypy core/

# Format code
poetry run black core/
```

## Architecture

This shared library follows the **Dependency Inversion Principle**:
- Services depend on abstractions (this library)
- State models define contracts between agents
- Logger provides consistent observability

```
┌─────────────┐  ┌──────────────┐  ┌───────────┐
│ Orchestrator│  │ Browser Agent│  │ ML Worker │
└──────┬──────┘  └──────┬───────┘  └─────┬─────┘
       │                │                 │
       └────────────────┼─────────────────┘
                        │
                 ┌──────▼──────┐
                 │ Core Library│
                 │ (State, Log)│
                 └─────────────┘
```

## License

See main project LICENSE.
