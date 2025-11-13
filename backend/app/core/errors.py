"""Error reporting and tracking."""
import os
from typing import Any, Dict, Optional

from app.core.logging import get_logger

logger = get_logger(__name__)

# Global Sentry instance
_sentry_initialized = False


def init_error_reporting() -> None:
    """
    Initialize error reporting (Sentry).
    
    Requires SENTRY_DSN environment variable to be set.
    If not set, errors will only be logged locally.
    """
    global _sentry_initialized
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    
    if not sentry_dsn:
        logger.info("SENTRY_DSN not set - error reporting disabled (local logging only)")
        return
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        # Get environment and release info
        environment = os.getenv("ENVIRONMENT", "development")
        release = os.getenv("APP_VERSION", "unknown")
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            release=release,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
            # Adjust this value in production
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
        )
        
        _sentry_initialized = True
        logger.info(f"Sentry initialized successfully (environment: {environment}, release: {release})")
        
    except ImportError:
        logger.warning("Sentry SDK not installed - install with: pip install sentry-sdk")
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def report_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    level: str = "error",
) -> None:
    """
    Report an error to Sentry (if configured) and log it.
    
    Args:
        error: The exception to report
        context: Additional context data (user_id, request_id, etc.)
        level: Error level (debug, info, warning, error, fatal)
    """
    # Always log the error locally
    logger.error(f"Error: {error}", exc_info=True, extra=context or {})
    
    # Send to Sentry if initialized
    if _sentry_initialized:
        try:
            import sentry_sdk
            
            # Add context to Sentry
            if context:
                for key, value in context.items():
                    sentry_sdk.set_context(key, value)
            
            # Capture the exception
            sentry_sdk.capture_exception(error, level=level)
            
        except Exception as e:
            logger.error(f"Failed to report error to Sentry: {e}")


def report_message(
    message: str,
    context: Optional[Dict[str, Any]] = None,
    level: str = "info",
) -> None:
    """
    Report a message to Sentry (if configured) and log it.
    
    Useful for tracking important events without an exception.
    
    Args:
        message: The message to report
        context: Additional context data
        level: Message level (debug, info, warning, error, fatal)
    """
    # Log the message
    log_level = getattr(logger, level.lower(), logger.info)
    log_level(message, extra=context or {})
    
    # Send to Sentry if initialized
    if _sentry_initialized:
        try:
            import sentry_sdk
            
            # Add context to Sentry
            if context:
                for key, value in context.items():
                    sentry_sdk.set_context(key, value)
            
            # Capture the message
            sentry_sdk.capture_message(message, level=level)
            
        except Exception as e:
            logger.error(f"Failed to report message to Sentry: {e}")


def set_user_context(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """
    Set user context for error reporting.
    
    Args:
        user_id: User identifier
        email: User email (optional)
        username: Username (optional)
    """
    if _sentry_initialized:
        try:
            import sentry_sdk
            
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username,
            })
        except Exception as e:
            logger.error(f"Failed to set user context: {e}")

