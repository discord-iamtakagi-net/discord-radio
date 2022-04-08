from __future__ import annotations

from dataclasses import dataclass
import os

@dataclass
class Env():
    BOT_TOKEN: str
    RADIKO_MAIL: str
    RADIKO_PASS: str
    STATION_ID: str
    VOICE_CHANNEL_ID: int

    @staticmethod
    def load() -> Env:
        return Env (
            BOT_TOKEN = os.getenv("BOT_TOKEN"),
            RADIKO_MAIL = os.getenv("RADIKO_MAIL"),
            RADIKO_PASS = os.getenv("RADIKO_PASS"),
            STATION_ID = os.getenv("STATION_ID"),
            VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID"))
        )