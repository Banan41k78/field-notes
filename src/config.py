"""
Центральный конфиг приложения.
Все настройки, которые пользователь может менять через экран «Настройки».
Значения по умолчанию заданы здесь, реальные — хранятся в page.client_storage.
"""

from dataclasses import dataclass, field, asdict, fields, is_dataclass
from enum import Enum
import json
import typing
import copy
import flet as ft

# ============================================================
#  ENUMS — фиксированные варианты значений
# ============================================================

class GPSAccuracy(str, Enum):
    HIGH = "high"          # GPS, точность ±3-5 м, больше расход батареи
    BALANCED = "balanced"  # компромисс
    LOW = "low"            # по Wi-Fi/сотам, экономия батареи


class MapProvider(str, Enum):
    OSM = "osm"
    YANDEX = "yandex"
    SATELLITE = "satellite"


class ThemeMode(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class DistanceUnit(str, Enum):
    KM = "km"
    MILES = "miles"


class SpeedUnit(str, Enum):
    KMH = "kmh"
    MPH = "mph"


class AltitudeUnit(str, Enum):
    METERS = "m"
    FEET = "ft"


class CoordFormat(str, Enum):
    DD = "dd"     # десятичные градусы: 55.751244
    DMS = "dms"   # градусы-минуты-секунды: 55°45'04"N


class AutoDeletePolicy(str, Enum):
    NEVER = "never"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"


# ============================================================
#  СЕКЦИИ НАСТРОЕК
# ============================================================

@dataclass
class GPSSettings:
    """Локальные настройки устройства. НЕ синхронизируются."""
    accuracy: GPSAccuracy = GPSAccuracy.BALANCED
    distance_filter: int = 5            # метров между точками трека
    auto_pause: bool = True
    auto_pause_threshold_kmh: float = 0.5
    auto_pause_duration_sec: int = 120  # 2 минуты
    record_in_background: bool = True
    keep_screen_on: bool = True
    # звук/вибро
    sound_on_start: bool = True
    sound_on_pause: bool = True
    sound_on_stop: bool = True
    sound_on_gps_lost: bool = True
    vibrate: bool = True


@dataclass
class MapSettings:
    """Локальные настройки карты. НЕ синхронизируются."""
    provider: MapProvider = MapProvider.OSM
    yandex_api_key: str = ""            # лучше хранить в client_storage отдельно
    show_traffic: bool = False
    tile_quality: str = "standard"      # standard | hd
    auto_load_tiles_wifi: bool = True


@dataclass
class SyncSettings:
    """Могут синхронизироваться с сервером, но в первую очередь — локальны."""
    auto_sync: bool = True
    wifi_only: bool = True
    sync_tracks: bool = True
    sync_routes: bool = True
    sync_settings: bool = False          # настройки — в основном локальны
    server_url: str = ""
    last_sync_iso: str = ""             # время последней синхронизации


@dataclass
class NotificationSettings:
    """Локальные. НЕ синхронизируются."""
    show_recording_notification: bool = True
    warn_gps_lost: bool = True
    warn_route_deviation: bool = True
    route_deviation_threshold_m: int = 100
    low_battery_threshold: int = 15     # %


@dataclass
class UnitSettings:
    """Локальные, но могут синхронизироваться — привычки пользователя."""
    distance: DistanceUnit = DistanceUnit.KM
    speed: SpeedUnit = SpeedUnit.KMH
    altitude: AltitudeUnit = AltitudeUnit.METERS
    coordinates: CoordFormat = CoordFormat.DD


@dataclass
class DisplaySettings:
    """Локальные. НЕ синхронизируются."""
    theme: ThemeMode = ThemeMode.SYSTEM
    large_font: bool = False
    show_track_on_map: bool = True
    show_route_on_map: bool = True
    show_waypoints: bool = True


@dataclass
class DataSettings:
    """Локальные. НЕ синхронизируются."""
    auto_delete_old_tracks: AutoDeletePolicy = AutoDeletePolicy.NEVER
    analytics_enabled: bool = False


# ============================================================
#  КОРНЕВОЙ КОНТЕЙНЕР
# ============================================================

@dataclass
class AppSettings:
    gps: GPSSettings = field(default_factory=GPSSettings)
    maps: MapSettings = field(default_factory=MapSettings)
    sync: SyncSettings = field(default_factory=SyncSettings)
    notifications: NotificationSettings = field(default_factory=NotificationSettings)
    units: UnitSettings = field(default_factory=UnitSettings)
    display: DisplaySettings = field(default_factory=DisplaySettings)
    data: DataSettings = field(default_factory=DataSettings)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, raw: dict) -> "AppSettings":
        """Восстанавливает объект из словаря, рекурсивно обрабатывая enum и вложенные dataclass."""
        return _rebuild(cls, raw)


# ============================================================
#  ВНУТРЕННИЕ ХЕЛПЕРЫ
# ============================================================

def _rebuild(cls, data: dict):
    """Рекурсивно восстанавливает dataclass из dict, корректно обрабатывая Enum."""
    if not isinstance(data, dict):
        return data

    type_hints = typing.get_type_hints(cls)
    kwargs = {}

    for f in fields(cls):
        if f.name not in data:
            continue

        value = data[f.name]
        target_type = type_hints[f.name]

        # Разворачиваем Optional[X] → X
        origin = typing.get_origin(target_type)
        if origin is typing.Union:
            args = [a for a in typing.get_args(target_type) if a is not type(None)]
            if args:
                target_type = args[0]

        if isinstance(target_type, type) and issubclass(target_type, Enum):
            try:
                kwargs[f.name] = target_type(value)
            except ValueError:
                # если в файле битое значение — оставляем дефолт
                pass
        elif is_dataclass(target_type):
            kwargs[f.name] = _rebuild(target_type, value)
        else:
            kwargs[f.name] = value

    return cls(**kwargs)


# ============================================================
#  ЗАГРУЗКА / СОХРАНЕНИЕ
# ============================================================

STORAGE_KEY = "app.settings"


async def load_settings(prefs: ft.SharedPreferences) -> AppSettings:
    """Загружает настройки. prefs — уже созданный и привязанный сервис."""
    raw = await prefs.get(STORAGE_KEY)
    if not raw:
        return AppSettings()
    try:
        return AppSettings.from_dict(json.loads(raw))
    except (json.JSONDecodeError, TypeError, ValueError):
        return AppSettings()


async def save_settings(prefs: ft.SharedPreferences, settings: AppSettings) -> None:
    """Сохраняет настройки."""
    await prefs.set(STORAGE_KEY, settings.to_json())


async def reset_settings(page: ft.Page) -> AppSettings:
    """Сбрасывает настройки."""
    prefs = ft.SharedPreferences()
    await prefs.remove(STORAGE_KEY)
    return AppSettings()