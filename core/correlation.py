"""Correlation ID management for request tracing across services."""
import uuid
from contextvars import ContextVar
from typing import Optional
from functools import wraps

# Context variable to store correlation ID thread-safe
_correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

# Header name for correlation ID
CORRELATION_ID_HEADER = "x-correlation-id"
CORRELATION_ID_LENGTH = 16


def generate_correlation_id() -> str:
    """Generate a new correlation ID.
    
    Format: short-alphanumeric prefix + random suffix
    Example: webhook-a1b2c3d4e5f6g7h8
    """
    return f"webhook-{uuid.uuid4().hex[:CORRELATION_ID_LENGTH]}"


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context.
    
    Returns None if not set.
    """
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in context.
    
    Thread-safe via contextvars.
    """
    _correlation_id_ctx.set(correlation_id)


def clear_correlation_id() -> None:
    """Clear the correlation ID from context."""
    _correlation_id_ctx.set(None)


def correlateLogger(func):
    """Decorator to add correlation_id to function logs.
    
    Usage:
        @correlateLogger
        def my_function():
            logger.info("message")  # Will include correlation_id
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        correlation_id = get_correlation_id()
        if correlation_id:
            # Add correlation_id to logging context
            from core.logger import logger
            return logger.bind(correlation_id=correlation_id)
        return func(*args, **kwargs)
    
    return wrapper


class CorrelationContext:
    """Context manager for correlation ID.
    
    Usage:
        with CorrelationContext("my-correlation-id") as ctx:
            logger.info("message")  # Includes correlation_id
    """
    
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or generate_correlation_id()
        self.previous_id: Optional[str] = None
    
    def __enter__(self):
        self.previous_id = get_correlation_id()
        set_correlation_id(self.correlation_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_id is not None:
            set_correlation_id(self.previous_id)
        else:
            clear_correlation_id()
        return False


def get_logger_with_correlation():
    """Get a logger that includes correlation_id in all logs.
    
    Usage:
        logger = get_logger_with_correlation()
        logger.info("message")  # Includes correlation_id if set
    """
    from structlog import get_logger
    from core.logger import logger as base_logger
    
    correlation_id = get_correlation_id()
    if correlation_id:
        return base_logger.bind(correlation_id=correlation_id)
    return base_logger