from contextvars import ContextVar
from typing import Dict

# Request-scoped context variable to hold user-specific API keys
request_api_keys: ContextVar[Dict[str, str]] = ContextVar("request_api_keys", default={})
