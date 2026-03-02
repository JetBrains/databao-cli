from logging.config import dictConfig


def configure_logging():
    dictConfig(
        {
            "version": 1,
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                },
            },
            "loggers": {
                "databao_context_engine": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": ["stdout"],
                },
                "databao_cli": {
                    "level": "INFO",
                    "propagate": False,
                    "handlers": ["stderr"],
                },
            },
        }
    )
