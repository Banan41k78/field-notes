"""Сохранение и чтение треков из FLET_APP_STORAGE_DATA."""
from __future__ import annotations

import json
import os
from pathlib import Path

from models.track import Track


def _data_dir() -> Path:
    base = os.getenv("FLET_APP_STORAGE_DATA")
    if not base:
        base = Path.home() / ".field_notes" / "data"
    path = Path(base) / "tracks"
    path.mkdir(parents=True, exist_ok=True)
    return path


class TrackStorage:
    def __init__(self, data_dir: Path | None = None):
        self._dir = data_dir or _data_dir()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, track_id: str) -> Path:
        return self._dir / f"{track_id}.json"

    def save(self, track: Track) -> None:
        path = self._path(track.id)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(track.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(path)

    def get(self, track_id: str) -> Track | None:
        path = self._path(track_id)
        if not path.exists():
            return None
        try:
            return Track.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            return None

    def list(self) -> list[Track]:
        tracks: list[Track] = []
        for path in self._dir.glob("*.json"):
            try:
                tracks.append(
                    Track.from_dict(json.loads(path.read_text(encoding="utf-8")))
                )
            except (json.JSONDecodeError, TypeError, ValueError, KeyError):
                continue
        tracks.sort(key=lambda t: t.created_at, reverse=True)
        return tracks

    def delete(self, track_id: str) -> bool:
        path = self._path(track_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def count(self) -> int:
        return sum(1 for _ in self._dir.glob("*.json"))