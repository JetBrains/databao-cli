def child_answer(child, pattern: str, value: str | None) -> None:
    child.expect(pattern)
    child.sendline("" if value is None else str(value))


def child_answer_safe(child, pattern: str, value: str | None) -> None:
    child.expect(pattern)
    send_secret(child, "" if value is None else str(value))


def send_secret(child, value: str):
    old = child.logfile
    child.logfile = None
    child.sendline(value)
    child.logfile = old
