from datetime import datetime
from logging.config import dictConfig
from pathlib import Path
from typing import Any

from databao_cli.project.layout import ProjectLayout


def configure_logging(project_layout: ProjectLayout | None) -> None:
    log_config = {
        "version": 1,
        "formatters": {
            "file": {
                "format": "%(asctime)s %(levelname)s %(name)s: %(message)s"
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "INFO"
            },
            "stderr": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "databao_context_engine": {
                "level": "DEBUG",
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

    if project_layout:
        logs_dir = project_layout.logs_dir
        logs_dir.mkdir(exist_ok=True)

        file_handler_name = "logFile"
        log_config["handlers"][file_handler_name] = _get_logging_file_handler(logs_dir)
        log_config["loggers"]["databao_context_engine"]["handlers"].append(file_handler_name)
    dictConfig(log_config)


def _get_logging_file_handler(logs_dir: Path) -> dict[str, Any]:
    return {
        "filename": str(logs_dir.joinpath(_get_current_log_filename())),
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "file",
        "maxBytes": 100_000_000,  # 100MB
        "backupCount": 12,
        "level": "DEBUG",
    }

def _get_current_log_filename() -> str:
    # Creates a new log file every month
    return datetime.now().strftime("log-%Y-%m.txt")
