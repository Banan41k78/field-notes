"""Импорт и экспорт GPX."""
from __future__ import annotations

from datetime import datetime

import gpxpy
import gpxpy.gpx

from models.route import Route, RoutePoint
from models.track import Track, TrackPoint


# ---------- Импорт ----------

def parse_gpx_to_route(path: str, name: str | None = None) -> Route | None:
    """
    Прочитать GPX-файл и вернуть Route.
    Берёт первую траекторию/маршрут из файла.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
    except (OSError, gpxpy.gpx.GPXException, ValueError):
        return None

    points: list[RoutePoint] = []

    # 1. Треки (trk)
    for trk in gpx.tracks:
        for seg in trk.segments:
            for pt in seg.points:
                points.append(RoutePoint(
                    lat=pt.latitude,
                    lon=pt.longitude,
                    name=None,
                    description=None,
                ))
        break  # только первый trk

    # 2. Если треков нет — пробуем маршруты (rte)
    if not points:
        for rte in gpx.routes:
            for pt in rte.points:
                points.append(RoutePoint(
                    lat=pt.latitude,
                    lon=pt.longitude,
                    name=pt.name,
                    description=pt.description,
                ))
            break

    # 3. Если пусто — пробуем путевые точки (wpt)
    if not points:
        for wpt in gpx.waypoints:
            points.append(RoutePoint(
                lat=wpt.latitude,
                lon=wpt.longitude,
                name=wpt.name,
                description=wpt.description,
            ))

    if len(points) < 2:
        return None

    route_name = name or (gpx.tracks[0].name if gpx.tracks else None) or "Импорт GPX"
    return Route(
        name=route_name,
        points=points,
        source="gpx",
        created_at=datetime.now().isoformat(timespec="seconds"),
    )


def parse_gpx_to_track(path: str, name: str | None = None) -> Track | None:
    """Прочитать GPX-файл и вернуть Track (записанный трек)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
    except (OSError, gpxpy.gpx.GPXException, ValueError):
        return None

    points: list[TrackPoint] = []
    for trk in gpx.tracks:
        for seg in trk.segments:
            for pt in seg.points:
                points.append(TrackPoint(
                    lat=pt.latitude,
                    lon=pt.longitude,
                    timestamp=pt.time.isoformat() if pt.time else datetime.now().isoformat(),
                    altitude=pt.elevation,
                    speed_kmh=None,
                ))
        break

    if len(points) < 2:
        return None

    track_name = name or (gpx.tracks[0].name if gpx.tracks else None) or "Импорт GPX"
    return Track(
        name=track_name,
        points=points,
        created_at=datetime.now().isoformat(timespec="seconds"),
    )


# ---------- Экспорт ----------

def route_to_gpx_string(route: Route) -> str:
    """Сериализовать Route в GPX-строку."""
    gpx = gpxpy.gpx.GPX()
    gpx.creator = "Field Notes"

    gpx_track = gpxpy.gpx.GPXTrack(name=route.name or "Маршрут")
    gpx.tracks.append(gpx_track)
    seg = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(seg)

    for p in route.points:
        seg.points.append(gpxpy.gpx.GPXTrackPoint(
            latitude=p.lat,
            longitude=p.lon,
            name=p.name,
            description=p.description,
        ))

    return gpx.to_xml()


def track_to_gpx_string(track: Track) -> str:
    """Сериализовать Track в GPX-строку."""
    gpx = gpxpy.gpx.GPX()
    gpx.creator = "Field Notes"

    gpx_track = gpxpy.gpx.GPXTrack(name=track.name or "Трек")
    gpx.tracks.append(gpx_track)
    seg = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(seg)

    for p in track.points:
        try:
            t = datetime.fromisoformat(p.timestamp)
        except (ValueError, TypeError):
            t = None
        seg.points.append(gpxpy.gpx.GPXTrackPoint(
            latitude=p.lat,
            longitude=p.lon,
            elevation=p.altitude,
            time=t,
        ))

    return gpx.to_xml()


def export_route_to_file(route: Route, path: str) -> bool:
    """Сохранить Route в GPX-файл."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(route_to_gpx_string(route))
        return True
    except OSError:
        return False


def export_track_to_file(track: Track, path: str) -> bool:
    """Сохранить Track в GPX-файл."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(track_to_gpx_string(track))
        return True
    except OSError:
        return False