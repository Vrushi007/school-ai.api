# AI Agent Instructions for School AI API

## Project Overview

**School AI API** is a FastAPI-based service that generates CBSE/NCERT-aligned educational content using OpenAI. It's designed for Indian school standards with core features: lesson plan generation, detailed session content, and question paper creation.

## Architecture

### Core Services Layer

- **OpenAIService** (`services/openai_service.py`): Main abstraction for all OpenAI interactions. Returns `Tuple[bool, Dict, str]` - (success flag, parsed data/raw content, error message)
- **JSONParser** (`utils/json_parser.py`): Handles malformed AI responses gracefully. Cleans trailing commas, removes comments, extracts from markdown blocks
- **PromptTemplates** (`prompts.py`): Centralized system prompts that enforce JSON-only output for different content types

### Router Structure

Each router is a clean endpoint facade with minimal logic:

- `/api/generate-lesson-plan` → returns lesson overview with sessions list
- `/api/generate-detailed-content-for-session` → detailed content + YouTube resource integration
- `/api/generate-questions` → question papers with marks
- Student chatbot routes in `student.py`

**Key Pattern**: Routers call OpenAIService methods, receive parsed results, then return `APIResponse(success, data, message, error)` model.

### Environment & Configuration

- **config.py**: `OpenAIConfig` class loads `OPENAI_API_KEY` and `OPENAI_MODEL` from `.env`
- Default model: `gpt-4o-mini` (override via `OPENAI_MODEL` env var)
- Missing API key raises immediate `ValueError` on startup

## Critical Patterns

### Response Handling

All API endpoints return `APIResponse` model:

```python
APIResponse(success=True, data={"lesson_plan": parsed}, message="Success")
APIResponse(success=False, error="JSON parsing error: ...", data={"raw_response": raw})
```

On OpenAI failures, include `raw_response` in data for frontend debugging.

### JSON Parsing Strategy

1. OpenAI responses are expected as pure JSON (system prompt: "Respond only in JSON")
2. `JSONParser.extract_json_from_response()` handles markdown blocks and common errors
3. On parse failure, `fallback_to_raw=True` returns raw text so UI can debug
4. Never silently drop malformed responses—log errors and inform client

### Logging

- Use `logger = logging.getLogger(__name__)` in all modules
- Log at entry (`logger.info("Generating X...")`) and error points
- `openai_timing_logger` tracks API calls: duration, token count, success/failure, input size

### Error Handling

- **HTTP errors**: Caught by `http_exception_handler` in exceptions.py (returns JSON with success=False)
- **Unhandled exceptions**: Caught by `general_exception_handler` (returns 500 with generic message)
- **Configuration errors**: Raised immediately in config.py on missing API key (fail-fast)

## Development Workflows

### Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-minimal.txt
cp .env.example .env  # Add OPENAI_API_KEY=sk-...
python main.py  # Starts on localhost:8000
```

### Testing

- `test_api.py`: Manual endpoint testing (POST requests to lesson plan, questions, etc.)
- `test_json_parser.py`: Unit tests for JSON extraction and cleaning logic
- No automated test framework configured; tests are scripted for manual runs

### Running & Debugging

- **Local**: `python main.py` (uvicorn on :8000, reload disabled for macOS Python 3.13 stability)
- **Production**: Set `PORT` env var (e.g., Render platform)
- **Logs**: Check stdout; `openai_timing_logger` writes to `logs/` directory
- Debug slow responses: Check logs for token counts and API duration

## Project-Specific Conventions

1. **System Prompts**: Stored in `PromptTemplates` class, enforce "JSON only" output. Avoid ad-hoc prompts in routers.
2. **Field Naming**: Use snake_case for JSON requests/responses. Pydantic models enforce this.
3. **Session Data**: Always include `title`, `summary`, `duration`, `objectives` in session requests.
4. **Resource Integration**: Session content includes YouTube search (via `YouTubeHelper`) based on keywords from AI response.
5. **CBSE/NCERT Focus**: Prompts explicitly mention this. Content is age-appropriate for Indian school curriculum.

## Adding New Features

**New Endpoint Pattern**:

1. Add Pydantic model in `models.py` for request/response
2. Add system prompt in `PromptTemplates`
3. Add service method in `openai_service.py` (return `Tuple[bool, data, error]`)
4. Add router endpoint in appropriate file under `routers/` (call service, wrap in `APIResponse`)
5. Update `main.py` to include router if new file

**New Integration** (e.g., external API):

- Create helper in `helpers/` (e.g., `youtube.py` pattern)
- Call from router, not from service (services layer is OpenAI-only)
- Log all external API calls with timing

## Key Files to Reference

- [models.py](models.py) - All request/response schemas
- [services/openai_service.py](services/openai_service.py) - Service layer with error recovery
- [utils/json_parser.py](utils/json_parser.py) - JSON extraction and cleanup logic
- [routers/lesson_planning.py](routers/lesson_planning.py) - Reference router endpoint
- [config.py](config.py) - Environment setup and app initialization

## Common Pitfalls to Avoid

1. **Don't hardcode prompts** → Use PromptTemplates class
2. **Don't skip JSON error handling** → Always use JSONParser.extract_json_from_response()
3. **Don't log sensitive data** → Filter API keys from logs
4. **Don't call external APIs from services** → Services are OpenAI-only; use helpers
5. **Don't rely on reload mode** → macOS + Python 3.13 issue; test with `reload=False`
