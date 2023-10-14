import logging
from logging.config import dictConfig

from app.config import DevConfig, config


def obfuscated(email: str, obfuscated_length: int) -> str:
    """Obfuscates email addresses."""
    characters = email[:obfuscated_length]
    first, last = email.split("@")
    return characters + ("*" * (len(first) - obfuscated_length)) + "@" + last


class EmailObfuscatorFilter(logging.Filter):
    """Obfuscates email addresses in logs."""

    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        """Initializes the filter."""
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        """Obfuscates email addresses in logs."""
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscated_length)
        return True


def configure_logging() -> None:
    """Configure logging for the application."""
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    # function call
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    # arguments to the function call above:
                    "uuid_length": 8 if isinstance(config, DevConfig) else 32,
                    "default_value": "-",
                },
                "email_obfuscator": {
                    "()": "app.logging_config.EmailObfuscatorFilter",
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 0,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s: %(lineno)d in %(module)s: %(message)s",
                },
                "file": {
                    "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s.%(msecs)03dZ | %(levelname)-8s | [%(correlation_id)s] %(name)s:%(lineno)d - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscator"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": ["correlation_id", "email_obfuscator"],
                    "filename": "app.log",
                    "maxBytes": 1024 * 1024,
                    "backupCount": 2,
                    "encoding": "utf8",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default", "rotating_file"],
                    "level": "INFO",
                },
                "databases": {
                    "handlers": ["default", "rotating_file"],
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": ["default"],
                    "level": "WARNING",
                },
                "app": {
                    "handlers": ["default", "rotating_file"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,  # does not send any logs to its parent logger
                },
            },
        }
    )
