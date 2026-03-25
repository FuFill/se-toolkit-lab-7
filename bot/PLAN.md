# Development Plan: LMS Telegram Bot

## Overview

This document outlines the development plan for the LMS (Learning Management System) Telegram bot. The bot provides students with access to their academic data, including scores, lab assignments, and deadlines, through a conversational interface powered by LLM-based intent routing.

## Architecture

### Core Principles

1. **Testable handlers**: All command logic is isolated in handler functions that take input and return text responses. Handlers have no dependency on Telegram, enabling offline testing via `--test` mode.
2. **Separation of concerns**: Clear boundaries between handlers (command logic), services (API clients), and the entry point (Telegram integration).
3. **Configuration via environment**: All secrets and configuration values are loaded from environment variables via `.env.bot.secret`.
4. **LLM tool use**: The LLM decides which API endpoints to call based on user intent — no regex or keyword matching in the routing path.

### Directory Structure

```
bot/
├── bot.py                  # Entry point: Telegram startup + --test mode
├── handlers/               # Command handlers (no Telegram dependency)
│   ├── __init__.py
│   ├── start.py            # /start command
│   ├── help.py             # /help command
│   ├── health.py           # /health command
│   ├── labs.py             # /labs command
│   ├── scores.py           # /scores command
│   └── intent_router.py    # LLM-based intent routing (Task 3)
├── services/               # API clients
│   ├── __init__.py
│   ├── lms_api.py          # LMS API client (9 endpoints)
│   └── llm_client.py       # LLM client for intent routing
├── config.py               # Environment variable loading
├── pyproject.toml          # Bot dependencies
└── PLAN.md                 # This file
```

## Implementation Phases

### Phase 1: Scaffold (Task 1) ✅

Create the basic project structure with:

- Entry point (`bot.py`) with `--test` mode support
- Handler directory with placeholder handlers
- Configuration module for loading environment variables
- Development plan (this document)

**Deliverables**: `bot/bot.py`, `bot/handlers/`, `bot/config.py`, `bot/PLAN.md`

### Phase 2: Backend Integration (Task 2) ✅

Implement real handler logic:

- Connect handlers to the LMS API via the backend service
- Implement `/start`, `/help`, `/health`, `/labs`, `/scores` commands
- Add error handling for API failures
- Test all commands in `--test` mode before deployment

**Deliverables**: Working handlers with API integration

### Phase 3: Intent Routing (Task 3) ✅

Add LLM-based natural language understanding:

- Implement LLM client service for intent classification
- Create intent router that maps user messages to handlers
- Support natural language queries like "what labs are available"
- Add fallback handling for unrecognized intents
- Add inline keyboard buttons for common actions

**Deliverables**:

- `services/llm_client.py` — LLM client with tool calling support
- `services/lms_api.py` — Extended with 9 API endpoints
- `handlers/intent_router.py` — Intent routing with tool execution loop
- `bot.py` — Updated with inline buttons and natural language handling

### Phase 4: Deployment (Task 4)

Deploy and monitor the bot:

- Configure production environment on the VM
- Set up logging and error tracking
- Document deployment process
- Create runbook for common issues

**Deliverables**: Deployed bot, deployment documentation

## Testing Strategy

1. **Unit tests**: Test handlers in isolation with mocked API responses
2. **Test mode**: Manual testing via `--test` flag before each deployment
3. **Integration tests**: Verify API connectivity with the backend
4. **E2E tests**: Test bot behavior in Telegram after deployment

### Test Mode Examples

```bash
# Single-step queries
uv run bot.py --test "what labs are available"
uv run bot.py --test "show me scores for lab 4"
uv run bot.py --test "who are the top 5 students in lab 01"

# Multi-step queries
uv run bot.py --test "which lab has the lowest pass rate"
uv run bot.py --test "which group is doing best in lab 3"

# Fallback/edge cases
uv run bot.py --test "asdfgh"      # Gibberish — helpful message
uv run bot.py --test "hello"       # Greeting — friendly response
uv run bot.py --test "lab 4"       # Ambiguous — clarification
```

## Configuration

The bot requires the following environment variables (see `.env.bot.example`):

- `BOT_TOKEN`: Telegram bot authentication token
- `LMS_API_BASE_URL`: Base URL of the LMS API
- `LMS_API_KEY`: API key for LMS access
- `LLM_API_KEY`: API key for LLM service (intent routing)
- `LLM_API_BASE_URL`: Base URL for LLM API
- `LLM_API_MODEL`: Model name (e.g., "coder-model")

## Tool Definitions

The LLM has access to 9 tools (backend endpoints):

| Tool | Endpoint | Description |
|------|----------|-------------|
| `get_items()` | `GET /items/` | List all labs and tasks |
| `get_learners()` | `GET /learners/` | List enrolled students |
| `get_scores(lab)` | `GET /analytics/scores?lab=` | Score distribution |
| `get_pass_rates(lab)` | `GET /analytics/pass-rates?lab=` | Per-task pass rates |
| `get_timeline(lab)` | `GET /analytics/timeline?lab=` | Submissions per day |
| `get_groups(lab)` | `GET /analytics/groups?lab=` | Per-group scores |
| `get_top_learners(lab, limit)` | `GET /analytics/top-learners?lab=&limit=` | Top N learners |
| `get_completion_rate(lab)` | `GET /analytics/completion-rate?lab=` | Completion rate % |
| `trigger_sync()` | `POST /pipeline/sync` | Refresh data from autochecker |

## Success Criteria

- All commands work in `--test` mode (exit code 0, non-empty output)
- Bot responds correctly in Telegram after deployment
- Handlers are testable without Telegram connection
- Configuration is loaded securely from environment variables
- LLM routes natural language queries to correct tools
- Multi-step queries work (LLM chains multiple API calls)
- Fallback handling for gibberish/unknown input

## Known Issues

- **Empty backend data**: If the ETL pipeline sync fails, all analytics endpoints return empty data. The bot handles this gracefully by informing the user that no data is available yet.
- **Qwen token expiration**: The Qwen Code OAuth token expires every few hours. Restart the proxy: `cd ~/qwen-code-oai-proxy && docker compose restart`.
