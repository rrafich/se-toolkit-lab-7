# Bot Development Plan
#popa popa popa
## Overview

This document outlines the development plan for the LMS Telegram Bot. The bot provides students with access to their learning management system data through a conversational interface in Telegram.

## Architecture

The bot follows a **separation of concerns** pattern with three layers:

1. **Transport Layer** (`bot.py`): Handles Telegram Bot API communication and CLI test mode
2. **Handler Layer** (`handlers/`): Command logic as pure functions (no Telegram dependency)
3. **Service Layer** (`services/`): External API clients (LMS API, LLM API)

This architecture enables **testable handlers** - the same handler functions work in test mode, unit tests, and production Telegram bot.

## Task Breakdown

### Task 1: Scaffold (Current)
- Create project structure with `bot.py`, `handlers/`, `services/`, `config.py`
- Implement `--test` mode for offline verification
- Write placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`

### Task 2: Backend Integration
- Implement `services/lms_client.py` to query the LMS API
- Connect `/health` to backend health endpoint
- Implement `/labs` to fetch available labs
- Implement `/scores` to fetch student scores

### Task 3: Intent-Based Routing
- Implement `services/llm_client.py` for LLM calls
- Create intent router that uses LLM to parse natural language queries
- Map intents like "what labs are available" to appropriate handlers
- Add tool descriptions for LLM to choose correct API calls

### Task 4: Deployment
- Create Dockerfile for the bot
- Add bot service to `docker-compose.yml`
- Document deployment process
- Set up health checks and logging

## Configuration

The bot reads configuration from environment variables:
- `BOT_TOKEN`: Telegram bot token from BotFather
- `LMS_API_BASE_URL`: Backend API URL
- `LMS_API_KEY`: Backend API authentication key
- `LLM_API_BASE_URL`: LLM API URL (Qwen Code API)
- `LLM_API_KEY`: LLM API authentication key
- `LLM_API_MODEL`: Model name to use

## Testing Strategy

1. **Test Mode**: `--test "/command"` runs handlers directly without Telegram
2. **Unit Tests**: Test handlers in isolation with mocked services
3. **Integration Tests**: Test full flow with test Telegram bot

## Success Criteria

- All commands work in `--test` mode
- Bot responds in Telegram within 2 seconds
- Graceful error handling for API failures
- Clear error messages to users when services are unavailable
