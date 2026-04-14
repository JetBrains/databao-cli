import allure
from pexpect import TIMEOUT, spawn
from pexpect.popen_spawn import PopenSpawn


@allure.step("Answering prompt '{pattern}' with '{value}'")
def child_answer(child: PopenSpawn | spawn, pattern: str, value: str | None) -> None:
    try:
        child.expect(pattern)
    except TIMEOUT as e:
        raise AssertionError(f"Timed out while waiting for a prompt with the pattern {pattern}") from e
    child.sendline("" if value is None else str(value))


@allure.step("Answering sensitive prompt '{pattern}'")
def child_answer_safe(child: PopenSpawn | spawn, pattern: str, value: str | None) -> None:
    try:
        child.expect(pattern)
    except TIMEOUT as e:
        raise AssertionError(f"Timed out while waiting for a prompt with the pattern {pattern}") from e
    send_secret(child, "" if value is None else str(value))


def send_secret(child: PopenSpawn | spawn, value: str):
    old = child.logfile
    child.logfile = None
    child.sendline(value)
    child.logfile = old
