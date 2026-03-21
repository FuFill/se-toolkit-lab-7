# Development Plan: LMS Telegram Bot

## Overview

This document outlines the development plan for the LMS (Learning Management System) Telegram bot. The bot provides students with access to their academic data, including scores, lab assignments, and deadlines, through a conversational interface powered by LLM-based intent routing.

## Architecture

### Core Principles

1. **Testable handlers**: All command logic is isolated in handler functions that take input and return text responses. Handlers have no dependency on Telegram, enabling offline testing via `--test` mode.
2. **Separation of concerns**: Clear boundaries between handlers (command logic), services (API clients), and the entry point (Telegram integration).
3. **Configuration via environment**: All secrets and configuration values are loaded from environment variables via `.env.bot.secret`.

### Directory Structure

```
bot/
├── bot.py              # Entry point: Telegram startup + --test mode
├── handlers/           # Command handlers (no Telegram dependency)
│   ├── __init__.py
│   ├── start.py        # /start command
│   ├── help.py         # /help command
│   ├── health.py       # /health command
│   └── labs.py         # /labs command
├── services/           # API clients
│   ├── __init__.py
│   ├── lms_api.py      # LMS API client
│   └── llm_client.py   # LLM client for intent routing
├── config.py           # Environment variable loading
├── pyproject.toml      # Bot dependencies
└── PLAN.md             # This file
```

## Implementation Phases

### Phase 1: Scaffold (Task 1)

Create the basic project structure with:
- Entry point (`bot.py`) with `--test` mode support
- Handler directory with placeholder handlers
- Configuration module for loading environment variables
- Development plan (this document)

**Deliverables**: `bot/bot.py`, `bot/handlers/`, `bot/config.py`, `bot/PLAN.md`

### Phase 2: Backend Integration (Task 2)

Implement real handler logic:
- Connect handlers to the LMS API via the backend service
- Implement `/start`, `/help`, `/health`, `/labs`, `/scores` commands
- Add error handling for API failures
- Test all commands in `--test` mode before deployment

**Deliverables**: Working handlers with API integration

### Phase 3: Intent Routing (Task 3)

Add LLM-based natural language understanding:
- Implement LLM client service for intent classification
- Create intent router that maps user messages to handlers
- Support natural language queries like "what labs are available"
- Add fallback handling for unrecognized intents

**Deliverables**: `services/llm_client.py`, intent routing logic

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

## Configuration

The bot requires the following environment variables (see `.env.bot.example`):

- `BOT_TOKEN`: Telegram bot authentication token
- `LMS_API_BASE_URL`: Base URL of the LMS API
- `LMS_API_KEY`: API key for LMS access
- `LLM_API_KEY`: API key for LLM service (intent routing)
- `LLM_API_BASE_URL`: Base URL for LLM API

## Success Criteria

- All commands work in `--test` mode (exit code 0, non-empty output)
- Bot responds correctly in Telegram after deployment
- Handlers are testable without Telegram connection
- Configuration is loaded securely from environment variables
