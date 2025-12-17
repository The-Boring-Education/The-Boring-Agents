# The Boring Agents

AI-powered content generation API for The Boring Education platform.

## Overview

The Boring Agents is a FastAPI-based service that provides AI-powered content generation capabilities through REST APIs. All operations are called from the Admin UI and logged comprehensively for monitoring and debugging.

## Quick Start

### Prerequisites

1. **Python 3.9+** installed (recommended to use a virtualenv)
2. **API Keys** configured in `.env` file:
    ```bash
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    HUGGINGFACE_API_KEY=your_huggingface_key
    ```

### Installation

1. **Clone and setup**:

    ```bash
    git clone <repository-url>
    cd The-Boring-Agents

    # Create & activate virtualenv (macOS/Linux)
    python3 -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt

    # If you see "ModuleNotFoundError: pydantic_settings"
    pip install pydantic-settings
    ```

2. **Configure environment**:

    Create a `.env` file in the repo root (at least one provider key is required):

    ```bash
    cat > .env <<'EOF'
    # AI Provider Keys (provide at least one)
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    HUGGINGFACE_API_KEY=your_huggingface_key

    # App behavior
    ENVIRONMENT=dev
    DEFAULT_MODEL=gpt-4o-mini
    MAX_TOKENS=4000
    TEMPERATURE=0.8
    OUTPUT_DIR=./output
    TEMP_DIR=./temp
    LOG_DIR=./logs

    # Local Agents API server controls
    AGENTS_API_HOST=0.0.0.0
    AGENTS_API_PORT=8088
    RELOAD=1

    # Backend URLs used for uploads (optional)
    LOCAL_API_BASE_URL=http://localhost:3000
    DEV_API_BASE_URL=https://tbe-dev-git-development-tbe.vercel.app
    PROD_API_BASE_URL=https://www.theboringeducation.com
    EOF
    ```

### Start the Agents API (FastAPI)

```bash
# From repo root
source .venv/bin/activate
export OPENAI_API_KEY=...  # set at least one provider key, or use .env

# Optional: override host/port
export AGENTS_API_HOST=0.0.0.0
export AGENTS_API_PORT=8088

python3 run.py  # FastAPI on http://localhost:8088
# Swagger UI: http://localhost:8088/docs
```

### Start the Agents API with Docker

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Access the API
curl http://localhost:8088/health
curl http://localhost:8088/api/v1/ping
```

**Note**: Make sure to set your API keys in the `.env` file or in `docker-compose.yml` environment variables before starting the container.

## File Structure

```
The-Boring-Agents/
├── lab/
│   └── interview-prep/          # Interview preparation files
│       ├── dsa_requirements.mdx     # Requirements for DSA interviews
│       ├── dsa_questions.mdx        # DSA questions list
│       ├── dsa_questions_with_metadata.mdx  # Questions with metadata
│       └── test_questions.mdx       # Test file for quick testing
├── src/
│   ├── agents/                 # AI agents for different tasks
│   │   ├── interview/          # Interview preparation agents
│   │   ├── project/           # Project generation agents
│   │   ├── quiz/              # Quiz generation agents
│   │   └── shiksha/           # Course creation agents
│   ├── api/                   # API routes and middleware
│   │   ├── middleware.py      # Request/response logging middleware
│   │   ├── logging_config.py  # Centralized logging configuration
│   │   ├── quiz_routes.py     # Quiz generation endpoints
│   │   ├── interview_routes.py # Interview preparation endpoints
│   │   └── sessions_routes.py # Session management endpoints
│   ├── core/                  # Core functionality
│   │   ├── env.py             # Environment variable management
│   │   └── config.py           # Configuration management
│   └── utils/                 # Utility functions
├── output/                    # Generated content output
├── logs/                      # API logs (rotated)
├── run.py                     # API server entry point
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
└── requirements.txt           # Python dependencies
```

## API Documentation

### Base URL

- **Local**: `http://localhost:8088`
- **Development**: Configure via `DEV_API_BASE_URL`
- **Production**: Configure via `PROD_API_BASE_URL`

### API Endpoints

#### Health & Status

- `GET /health` - Health check endpoint
- `GET /api/v1/ping` - Service ping with version info

#### Quiz Generation

- `GET /api/v1/quiz/topics` - Get available quiz topics
- `POST /api/v1/quiz/generate` - Generate a complete quiz
- `POST /api/v1/quiz/validate` - Validate quiz structure
- `POST /api/v1/quiz/upload` - Upload quiz to database
- `GET /api/v1/quiz/sessions` - List active quiz sessions
- `GET /api/v1/quiz/progress/{session_id}` - Get quiz generation progress
- `GET /api/v1/quiz/logs/{session_id}` - Get quiz session logs
- `GET /api/v1/quiz/pending` - List pending quiz files
- `GET /api/v1/quiz/pending/{filename}/content` - Get pending quiz content
- `DELETE /api/v1/quiz/pending/{filename}` - Delete pending quiz file

#### Interview Preparation

- `POST /api/v1/interview/create-sheet` - Create interview sheet from MDX
- `POST /api/v1/interview/generate-topic` - Generate questions for a topic
- `POST /api/v1/interview/bulk-generate` - Bulk generate for multiple topics
- `GET /api/v1/interview/sessions` - List interview sessions
- `GET /api/v1/interview/session/{session_id}/progress` - Get session progress
- `POST /api/v1/interview/session/{session_id}/cancel` - Cancel a session
- `POST /api/v1/interview/session/{session_id}/retry` - Retry a failed session
- `DELETE /api/v1/interview/session/{session_id}` - Delete a session
- `GET /api/v1/interview/topic-templates` - Get available topic templates
- `GET /api/v1/interview/roadmap-suggestions` - Get roadmap suggestions

#### Session Management

- `GET /api/v1/sessions/active` - List all active sessions (quiz + interview)
- `GET /api/v1/sessions/logs/{session_id}` - Get session logs
- `GET /api/v1/sessions/detail/{session_id}` - Get session detail
- `POST /api/v1/sessions/resume/{session_id}` - Resume a paused session
- `DELETE /api/v1/sessions/{session_id}` - Delete a session and its artifacts

### API Examples

#### Generate a Quiz

```bash
curl -X POST http://localhost:8088/api/v1/quiz/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "React",
    "question_count": 20,
    "target_audience": "developers",
    "save": true,
    "environment": "local"
  }'
```

#### Generate Interview Questions

```bash
curl -X POST http://localhost:8088/api/v1/interview/generate-topic \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "Python",
    "agentType": "tech",
    "technology": "Python",
    "questionCount": 25,
    "roadmap": "Backend",
    "difficulty": "Medium",
    "generateAnswers": true
  }'
```

#### Check Session Progress

```bash
curl http://localhost:8088/api/v1/quiz/progress/{session_id}
```

#### Get Session Logs

```bash
curl http://localhost:8088/api/v1/sessions/logs/{session_id}?limit=100
```

## Logging

The API provides comprehensive structured logging for all operations. All logs are written in JSON format for easy parsing and analysis.

### Log Locations

- **Console**: Structured JSON logs to stdout/stderr
- **File**: `logs/api.log` (rotated, 10MB per file, 5 backups)

### Log Format

All logs follow a structured JSON format:

```json
{
  "timestamp": "2024-12-17T22:43:13Z",
  "level": "INFO",
  "request_id": "uuid-here",
  "action": "generate_quiz",
  "topic": "React",
  "status": "success",
  "session_id": "abc123",
  "environment": "local"
}
```

### Log Levels

- **INFO**: Normal operations, request/response logging
- **WARNING**: Non-critical issues, validation failures
- **ERROR**: Errors, exceptions, failed operations
- **DEBUG**: Detailed debugging information (when enabled)

### Request Tracking

Every API request receives a unique `request_id` that is:
- Included in all logs related to that request
- Returned in response headers as `X-Request-ID`
- Used for tracing requests through the system

### Logging Features

- **Request/Response Logging**: All API requests and responses are logged with timing
- **Structured Format**: JSON format for easy parsing and analysis
- **Sensitive Data Masking**: API keys and secrets are automatically masked
- **Environment Context**: All logs include environment information
- **Session Tracking**: Session IDs are included in relevant logs
- **Error Tracking**: Full error details with stack traces for debugging

### Viewing Logs

```bash
# View live logs
tail -f logs/api.log

# View logs in JSON format
cat logs/api.log | jq

# Filter by request ID
cat logs/api.log | jq 'select(.request_id == "your-request-id")'

# Filter by action
cat logs/api.log | jq 'select(.action == "generate_quiz")'

# Filter errors
cat logs/api.log | jq 'select(.level == "ERROR")'
```

## Environment Variables

See `src/core/README.md` for detailed environment variable documentation.

### Key Variables

- `OPENAI_API_KEY` - OpenAI API key (at least one API key required)
- `ANTHROPIC_API_KEY` - Anthropic API key
- `HUGGINGFACE_API_KEY` - HuggingFace API key
- `ENVIRONMENT` - Environment: `local`, `dev`, or `prod`
- `LOG_LEVEL` - Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `AGENTS_API_HOST` - API server host (default: `0.0.0.0`)
- `AGENTS_API_PORT` - API server port (default: `8088`)
- `RELOAD` - Enable auto-reload for development (default: `1`)

## Configuration

### Environment Management

The system uses a centralized environment management module (`src/core/env.py`) that provides:

- Centralized environment variable loading
- Type-safe getters (str, int, bool, float)
- Comprehensive logging of environment loading
- Validation of required variables
- Sensitive data masking in logs

### Logging Configuration

Logging is configured in `src/api/logging_config.py` and provides:

- Structured JSON logging
- File rotation (10MB per file, 5 backups)
- Environment-based log levels
- Console and file handlers

## Development

### Running the Server

```bash
# Development mode (with auto-reload)
export RELOAD=1
python3 run.py

# Production mode
export RELOAD=0
python3 run.py
```

### API Documentation

- **Swagger UI**: `http://localhost:8088/docs`
- **ReDoc**: `http://localhost:8088/redoc`
- **OpenAPI JSON**: `http://localhost:8088/openapi.json`

### Testing API Endpoints

```bash
# Health check
curl http://localhost:8088/health

# Ping
curl http://localhost:8088/api/v1/ping

# Get available quiz topics
curl http://localhost:8088/api/v1/quiz/topics

# List active sessions
curl http://localhost:8088/api/v1/sessions/active
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t the-boring-agents .

# Run container
docker run -d \
  -p 8088:8088 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  -e OPENAI_API_KEY=your_key \
  the-boring-agents

# Or use docker-compose
docker-compose up -d
```

### Environment Variables in Docker

Set environment variables in `docker-compose.yml` or use a `.env` file:

```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  - ENVIRONMENT=prod
  - LOG_LEVEL=INFO
```

## Monitoring

### Health Checks

The API provides health check endpoints for monitoring:

```bash
# Basic health check
curl http://localhost:8088/health

# Service ping with version
curl http://localhost:8088/api/v1/ping
```

### Log Monitoring

Monitor logs for:
- Request/response patterns
- Error rates
- Performance metrics (duration_ms)
- Session tracking
- Environment-specific issues

### Request ID Tracking

Use the `X-Request-ID` header to track requests:

```bash
# Make request and capture request ID
curl -i -X POST http://localhost:8088/api/v1/quiz/generate \
  -H 'Content-Type: application/json' \
  -d '{"topic": "React", "question_count": 10}'

# Filter logs by request ID
cat logs/api.log | jq 'select(.request_id == "request-id-from-header")'
```

## Troubleshooting

### API Not Starting

1. Check environment variables are set
2. Verify API keys are configured
3. Check port 8088 is available
4. Review logs for errors

### No Logs Appearing

1. Check `LOG_DIR` environment variable
2. Verify write permissions for log directory
3. Check `LOG_LEVEL` is set appropriately
4. Review console output for errors

### API Keys Not Working

1. Verify keys are set in `.env` file
2. Check keys are not expired
3. Review logs for API key validation errors
4. Ensure at least one API key is configured

## Architecture

The system is built as a pure API service:

- **FastAPI** for the web framework
- **Structured JSON logging** for all operations
- **Request ID tracking** for traceability
- **Environment-aware** configuration
- **Docker-ready** for deployment

All operations are called via REST APIs from the Admin UI. No CLI interface is available.

## Support

For issues or questions:

1. Check the API health: `curl http://localhost:8088/health`
2. Review logs: `tail -f logs/api.log`
3. Check environment configuration: Review `.env` file
4. Verify API keys are configured correctly
