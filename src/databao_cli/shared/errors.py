class FeatureError(Exception):
    """Raised by feature functions to signal a user-facing error and request CLI exit."""

    def __init__(self, message: str, exit_code: int = 1) -> None:
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
