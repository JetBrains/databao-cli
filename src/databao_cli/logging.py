from logging.config import dictConfig


def configure_logging():
    dictConfig(
        {
            "version": 1,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {
                "databao_context_engine": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": ["console"],
                }
            },
        }
    )
