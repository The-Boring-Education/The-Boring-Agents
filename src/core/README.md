# Core Module Documentation

## Environment Variable Management

The `src.core.env` module provides a centralized, scalable way to handle environment variables with proper validation, logging, and type safety.

### Features

- ✅ **Centralized Management**: Single source of truth for all environment variables
- ✅ **Comprehensive Logging**: Detailed logging of environment loading and validation
- ✅ **Type Safety**: Type-safe getters for different data types (str, int, bool, float)
- ✅ **Validation**: Built-in validation for required variables and API keys
- ✅ **Scalable**: Easy to extend with new environment variables
- ✅ **Security**: Sensitive values (keys, secrets) are masked in logs

### Usage

#### Basic Usage

```python
from src.core.env import get_env, get_env_int, get_env_bool

# Get string value
log_level = get_env("LOG_LEVEL", "INFO")

# Get integer value
port = get_env_int("AGENTS_API_PORT", 8088)

# Get boolean value
reload = get_env_bool("RELOAD", True)
```

#### Using EnvironmentManager Directly

```python
from src.core.env import get_env_manager

env_manager = get_env_manager()

# Get values with type conversion
port = env_manager.get_int("AGENTS_API_PORT", 8088)
debug = env_manager.get_bool("DEBUG", False)

# Validate API keys
if env_manager.validate_api_keys():
    print("API keys configured")

# Log environment summary
env_manager.log_summary()
```

#### Using with Config (Recommended)

```python
from src.core.config import get_config

config = get_config()

# Access configuration values
print(config.environment)
print(config.api_base_url)
print(config.default_model)
```

### Environment File Loading Order

The environment manager loads variables in the following order (later files override earlier ones):

1. `.env.local` (local overrides, typically gitignored)
2. `.env` (default environment file)
3. System environment variables (highest priority)

### Available Environment Variables

#### API Keys (At least one required)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `HUGGINGFACE_API_KEY`

#### Application Settings
- `LOG_LEVEL` (default: "INFO")
- `OUTPUT_DIR` (default: "./output")
- `TEMP_DIR` (default: "./temp")
- `ENVIRONMENT` (default: "dev") - Options: "local", "dev", "prod"

#### Content Generation Settings
- `DEFAULT_MODEL` (default: "gpt-4o-mini")
- `MAX_TOKENS` (default: 4000)
- `TEMPERATURE` (default: 0.8)
- `MAX_CONTEXT_LENGTH` (default: 16000)

#### API Configuration
- `LOCAL_API_BASE_URL` (default: "http://localhost:3000")
- `DEV_API_BASE_URL` (default: "https://tbe-dev-git-development-tbe.vercel.app")
- `PROD_API_BASE_URL` (default: "https://www.theboringeducation.com")

#### Server Configuration
- `AGENTS_API_HOST` (default: "0.0.0.0")
- `AGENTS_API_PORT` (default: 8088)
- `RELOAD` (default: "1") - Enable auto-reload for development

### Logging

The environment manager provides comprehensive logging:

- **INFO**: Environment file loading, configuration summary
- **WARNING**: Missing optional variables, type conversion failures
- **ERROR**: Missing required variables, validation failures
- **DEBUG**: Individual variable retrieval (sensitive values masked)

### Validation

#### API Keys Validation

```python
from src.core.env import validate_api_keys

if not validate_api_keys():
    print("Error: No API keys configured")
```

#### Required Variables Validation

```python
from src.core.env import get_env_manager

env_manager = get_env_manager()
if not env_manager.validate_required():
    print("Error: Missing required environment variables")
```

### Best Practices

1. **Use `get_config()` for configuration**: The Config class provides a clean interface with type safety
2. **Use `get_env_*()` functions for server-specific settings**: Like port, host, reload mode
3. **Validate early**: Check API keys and required variables at application startup
4. **Log environment summary**: Use `env_manager.log_summary()` for debugging
5. **Don't log sensitive values**: The environment manager automatically masks API keys and secrets

### Migration Guide

If you're updating existing code:

**Before:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
port = int(os.getenv("PORT", "8088"))
```

**After:**
```python
from src.core.env import get_env_int

port = get_env_int("AGENTS_API_PORT", 8088)
```

**Before:**
```python
from src.core.config import config

if not config.validate_api_keys():
    # handle error
```

**After:**
```python
from src.core.env import validate_api_keys

if not validate_api_keys():
    # handle error
```

The `config` object still works for backward compatibility, but using the env module directly provides better logging and control.

