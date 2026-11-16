"""Сохранение и чтение маршрутов из FLET_APP_STORAGE_DATA."""
from __future__ import annotations

import json
import os
from pathlib import Path

from models.route import Route


def _data_dir() -> Path:
    base = os.getenv("FLET_APP_STORAGE_DATA")
    if not base:
        base = Path.home() / ".field_notes" / "data"
    path = Path(base) / "routes"
    path.mkdir(parents=True, exist_ok=True)
    return path


class RouteStorage:
    def __init__(self, data_dir: Path | None = None):
        self._dir = data_dir or _data_dir()
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, route_id: str) -> Path:
        return self._dir / f"{route_id}.json"

    def save(self, route: Route) -> None:
        path = self._path(route.id)
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(route.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(path)

    def get(self, route_id: str) -> Route | None:
        path = self._path(route_id)
        if not path.exists():
            return None
        try:
            return Route.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            return None

    def list(self) -> list[Route]:
        routes: list[Route] = []
        for path in self._dir.glob("*.json"):
            try:
                routes.append(
                    Route.from_dict(json.loads(path.read_text(encoding="utf-8")))
                )
            except (json.JSONDecodeError, TypeError, ValueError, KeyError):
                continue
        routes.sort(key=lambda r: r.created_at, reverse=True)
        return routes

    def delete(self, route_id: str) -> bool:
        path = self._path(route_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def count(self) -> int:
        return sum(1 for _ in self._dir.glob("*.json"))