import allure
from pexpect import spawn
from pexpect.popen_spawn import PopenSpawn


@allure.step("Answering prompt '{pattern}' with '{value}'")
def child_answer(child: PopenSpawn | spawn, pattern: str, value: str | None) -> None:
    child.expect(pattern)
    child.sendline("" if value is None else str(value))


@allure.step("Answering sensitive prompt '{pattern}'")
def child_answer_safe(child: PopenSpawn | spawn, pattern: str, value: str | None) -> None:
    child.expect(pattern)
    send_secret(child, "" if value is None else str(value))


def send_secret(child: PopenSpawn | spawn, value: str):
    old = child.logfile
    child.logfile = None
    child.sendline(value)
    child.logfile = old
