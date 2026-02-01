# CLAUDE.md - AI Assistant Guidelines for Tax Copilot API

## Project Overview

This is **Tax Copilot API** - a FastAPI backend for managing tax return case files with AI assistance. The system enables:
- CPA practitioners to create and manage structured tax case files
- CRUD operations on comprehensive tax return data
- LLM-powered agent integration for tax preparation assistance

**Current Version:** 0.1.0 (Early Development)

## Technology Stack

- **Language:** Python 3.8+
- **Framework:** FastAPI 0.110.2
- **Server:** Uvicorn 0.29.0
- **Database:** SQLite with SQLAlchemy 2.0.29 ORM
- **Validation:** Pydantic 1.10.14
- **AI Integration:** OpenAI API (GPT-4.1-mini)
- **Testing:** Pytest 8.2.1 with HTTPx

## Project Structure

```
hello-World/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── cases.py         # Case CRUD endpoints
│   │   └── agent.py         # LLM agent endpoints
│   └── services/
│       ├── __init__.py
│       └── llm.py           # OpenAI LLM integration
├── tests/
│   └── test_cases.py        # Integration tests
├── requirements.txt         # Python dependencies
├── README.md
└── CLAUDE.md                # This file
```

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload

# Run tests
pytest tests/

# Run specific test
pytest tests/test_cases.py -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/case` | Create new case |
| GET | `/case/{case_id}` | Retrieve case |
| PUT | `/case/{case_id}` | Full update |
| PATCH | `/case/{case_id}` | Partial update |
| POST | `/tax-agent/{case_id}` | Send message to AI agent |

## Code Conventions

### Python Style
- Use `from __future__ import annotations` for forward references
- Type hints are required on all function signatures
- Follow PEP 8 naming conventions

### FastAPI Patterns
- Use `APIRouter` with prefix and tags for route organization
- Use `Depends()` for dependency injection (e.g., database sessions)
- Return Pydantic models as `response_model` for validation
- Use appropriate HTTP status codes (201 for creation, 404 for not found, etc.)

### Database Patterns
- SQLite database stored at `./cases.db`
- Case data is stored as serialized JSON in the `data` column
- Use `get_db()` dependency for session management
- Use `serialize_case()` and `deserialize_case()` for JSON handling

### Error Handling
- Use `HTTPException` with proper status codes
- 404 for missing resources
- 400 for validation errors
- 502 for external service failures (LLM)

## Key Data Models

### CaseFile Schema (app/schemas.py)
The root model containing all tax-related data:
- `metadata` - Case ID, tax year, status, preparer info
- `taxpayer` - Primary person, spouse, filing status
- `dependents` - List of dependent information
- `income` - W2, 1099-INT, 1099-DIV, self-employment, rental, etc.
- `adjustments` - HSA, IRA contributions, student loan interest
- `deductions_and_credits` - Schedule A, child care, education, energy credits
- `withholding_and_payments` - Estimated payments, prior year refunds
- `documents` - Uploaded document metadata
- `issues_and_questions` - AI-identified issues and clarifications
- `preparer_review` - Final review checklist

### Filing Status Values
Valid options: `single`, `married_filing_joint`, `married_filing_separate`, `head_of_household`, `qualifying_widow`

### Case Status Values
- `intake_in_progress` - Initial data collection
- `ready_for_review` - Ready for CPA review
- `completed` - Filing complete

## LLM Service (app/services/llm.py)

The `LLMService` class handles AI integration:
- Requires `OPENAI_API_KEY` environment variable
- Falls back gracefully when API key is not configured
- Uses system prompt to act as US tax preparation copilot
- Returns structured JSON with `reply` and `updated_case_file`

## Testing Guidelines

- Tests use FastAPI's `TestClient`
- Test the full case lifecycle (create, get, update, agent interaction)
- Database is reset between test runs
- Agent endpoint works without real API key (uses fallback)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | No | OpenAI API key for LLM features |

## Important Notes for AI Assistants

1. **Database:** SQLite file `cases.db` is auto-created; don't check it into git
2. **Pydantic Version:** Uses Pydantic v1 syntax (`.dict()`, `.json()`, not `.model_dump()`)
3. **Case ID:** Auto-generated UUID stored in `metadata.id`
4. **JSON Storage:** Full case data is serialized as JSON, enabling flexible schema updates
5. **LLM Fallback:** System works without OpenAI API key with echo fallback
6. **No Authentication:** Currently no auth layer - intended for local/development use
7. **Import Pattern:** Use `from app import schemas` rather than importing individual classes
