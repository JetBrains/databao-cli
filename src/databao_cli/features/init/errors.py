class InitDatabaoProjectError(ValueError):
    def __init__(self, message: str | None):
        super().__init__(message or "")
        self.message = message


class DatabaoProjectDirAlreadyExistsError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ParentDatabaoProjectAlreadyExistsError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProjectDirDoesnotExistError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProjectDirNotDirError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaoContextEngineProjectInitError(InitDatabaoProjectError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
