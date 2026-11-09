"""Экран «Настройки»."""
import asyncio
from datetime import datetime
from app_context import AppContext
from views._nav import build_nav_bar

import flet as ft

from config import (
    AppSettings,
    GPSAccuracy, MapProvider, ThemeMode,
    DistanceUnit, SpeedUnit, AltitudeUnit, CoordFormat,
    AutoDeletePolicy,
    save_settings,
)


THEME_MAP = {
    ThemeMode.LIGHT: ft.ThemeMode.LIGHT,
    ThemeMode.DARK: ft.ThemeMode.DARK,
    ThemeMode.SYSTEM: ft.ThemeMode.SYSTEM,
}


def apply_theme(page: ft.Page, settings: AppSettings) -> None:
    page.theme_mode = THEME_MAP[settings.display.theme]


# ---------- Универсальные фабрики обработчиков ----------

def _bool_handler(settings, prefs, path: str):
    section, field = path.split(".")
    async def handler(e):
        setattr(getattr(settings, section), field, e.control.value)
        await save_settings(prefs, settings)
    return handler


def _enum_handler(settings, prefs, path: str, enum_cls):
    section, field = path.split(".")
    async def handler(e):
        try:
            setattr(getattr(settings, section), field, enum_cls(e.control.value))
            await save_settings(prefs, settings)
        except (ValueError, TypeError):
            pass
    return handler


def _int_handler(settings, prefs, path: str):
    section, field = path.split(".")
    async def handler(e):
        try:
            setattr(getattr(settings, section), field, int(e.control.value))
            await save_settings(prefs, settings)
        except (ValueError, TypeError):
            pass
    return handler


def _text_handler(settings, prefs, path: str, cast=str):
    section, field = path.split(".")
    async def handler(e):
        try:
            value = (e.control.value or "").strip()
            setattr(getattr(settings, section), field, cast(value) if value else None)
            await save_settings(prefs, settings)
        except (ValueError, TypeError):
            pass
    return handler


# ---------- Основной билдер ----------

def build_settings_content(ctx: AppContext) -> ft.View:
    page = ctx.page
    settings = ctx.settings
    prefs = ctx.prefs
    ref: dict = {}

    def rebuild():
        new_view = build_settings_content(ctx)
        idx = page.views.index(ref["view"])
        page.views[idx] = new_view
        page.update()

    # =============== GPS ===============
    gps_section = ft.ExpansionTile(
        title=ft.Text("GPS и запись"),
        subtitle=ft.Text("Точность, частота, автопауза"),
        leading=ft.Icon(ft.Icons.GPS_FIXED),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Dropdown(
                        label="Точность GPS",
                        value=settings.gps.accuracy.value,
                        options=[
                            ft.dropdown.Option(GPSAccuracy.HIGH.value, "Высокая"),
                            ft.dropdown.Option(GPSAccuracy.BALANCED.value, "Сбалансированная"),
                            ft.dropdown.Option(GPSAccuracy.LOW.value, "Экономная"),
                        ],
                        on_select=_enum_handler(settings, prefs, "gps.accuracy", GPSAccuracy),
                    ),
                    ft.Dropdown(
                        label="Записывать точку каждые … м",
                        value=str(settings.gps.distance_filter),
                        options=[ft.dropdown.Option(str(v), f"{v} м") for v in (1, 5, 10, 25, 50)],
                        on_select=_int_handler(settings, prefs, "gps.distance_filter"),
                    ),
                    ft.Switch(
                        label="Автопауза при остановке",
                        value=settings.gps.auto_pause,
                        on_change=_bool_handler(settings, prefs, "gps.auto_pause"),
                    ),
                    ft.TextField(
                        label="Порог автопаузы, км/ч",
                        value=str(settings.gps.auto_pause_threshold_kmh),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        on_blur=_text_handler(settings, prefs, "gps.auto_pause_threshold_kmh", float),
                    ),
                    ft.Switch(
                        label="Писать трек в фоне",
                        value=settings.gps.record_in_background,
                        on_change=_bool_handler(settings, prefs, "gps.record_in_background"),
                    ),
                    ft.Switch(
                        label="Не гасить экран при записи",
                        value=settings.gps.keep_screen_on,
                        on_change=_bool_handler(settings, prefs, "gps.keep_screen_on"),
                    ),
                    ft.Switch(
                        label="Вибрация при событиях",
                        value=settings.gps.vibrate,
                        on_change=_bool_handler(settings, prefs, "gps.vibrate"),
                    ),
                ], spacing=12),
            ),
        ],
    )

    # =============== Карты ===============
    maps_section = ft.ExpansionTile(
        title=ft.Text("Карты и офлайн"),
        subtitle=ft.Text("Провайдер, качество тайлов"),
        leading=ft.Icon(ft.Icons.MAP),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Dropdown(
                        label="Провайдер карт",
                        value=settings.maps.provider.value,
                        options=[
                            ft.dropdown.Option(MapProvider.OSM.value, "OpenStreetMap"),
                            ft.dropdown.Option(MapProvider.YANDEX.value, "Яндекс.Карты"),
                            ft.dropdown.Option(MapProvider.SATELLITE.value, "Спутник"),
                        ],
                        on_select=_enum_handler(settings, prefs, "maps.provider", MapProvider),
                    ),
                    ft.TextField(
                        label="API-ключ Яндекс.Карт",
                        value=settings.maps.yandex_api_key,
                        password=True,
                        can_reveal_password=True,
                        on_blur=_text_handler(settings, prefs, "maps.yandex_api_key"),
                    ),
                    ft.Dropdown(
                        label="Качество тайлов офлайн",
                        value=settings.maps.tile_quality,
                        options=[
                            ft.dropdown.Option("standard", "Стандарт"),
                            ft.dropdown.Option("hd", "HD"),
                        ],
                        on_select=_text_handler(settings, prefs, "maps.tile_quality"),
                    ),
                    ft.Switch(
                        label="Автозагрузка тайлов по Wi-Fi",
                        value=settings.maps.auto_load_tiles_wifi,
                        on_change=_bool_handler(settings, prefs, "maps.auto_load_tiles_wifi"),
                    ),
                    ft.Switch(
                        label="Показывать пробки",
                        value=settings.maps.show_traffic,
                        on_change=_bool_handler(settings, prefs, "maps.show_traffic"),
                    ),
                ], spacing=12),
            ),
        ],
    )

    # =============== Синхронизация ===============
    last_sync_label = ft.Text(
        f"Последняя синхронизация: {settings.sync.last_sync_iso or 'никогда'}",
        size=12,
        color=ft.Colors.GREY,
    )

    async def sync_now(e):
        e.control.disabled = True
        e.control.text = "Синхронизация…"
        e.control.update()
        try:
            await asyncio.sleep(1)  # TODO: заменить на реальный вызов API
            settings.sync.last_sync_iso = datetime.now().isoformat(timespec="seconds")
            await save_settings(prefs, settings)
        finally:
            e.control.text = "Синхронизировать сейчас"
            e.control.disabled = False
            e.control.update()
            last_sync_label.value = (
                f"Последняя синхронизация: {settings.sync.last_sync_iso or 'никогда'}"
            )
            last_sync_label.update()

    sync_button = ft.FilledButton(
        "Синхронизировать сейчас",
        icon=ft.Icons.CLOUD_SYNC,
        on_click=sync_now,
    )

    sync_section = ft.ExpansionTile(
        title=ft.Text("Синхронизация"),
        subtitle=last_sync_label,
        leading=ft.Icon(ft.Icons.SYNC),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Switch(
                        label="Автосинхронизация",
                        value=settings.sync.auto_sync,
                        on_change=_bool_handler(settings, prefs, "sync.auto_sync"),
                    ),
                    ft.Switch(
                        label="Только по Wi-Fi",
                        value=settings.sync.wifi_only,
                        on_change=_bool_handler(settings, prefs, "sync.wifi_only"),
                    ),
                    ft.Switch(
                        label="Синхронизировать треки",
                        value=settings.sync.sync_tracks,
                        on_change=_bool_handler(settings, prefs, "sync.sync_tracks"),
                    ),
                    ft.Switch(
                        label="Синхронизировать маршруты",
                        value=settings.sync.sync_routes,
                        on_change=_bool_handler(settings, prefs, "sync.sync_routes"),
                    ),
                    ft.TextField(
                        label="URL сервера (оставьте пустым для облака)",
                        value=settings.sync.server_url,
                        on_blur=_text_handler(settings, prefs, "sync.server_url"),
                    ),
                    sync_button,
                ], spacing=12),
            ),
        ],
    )

    # =============== Уведомления ===============
    notifications_section = ft.ExpansionTile(
        title=ft.Text("Уведомления"),
        subtitle=ft.Text("GPS, сход с маршрута, батарея"),
        leading=ft.Icon(ft.Icons.NOTIFICATIONS),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Switch(
                        label="Постоянное уведомление «Запись идёт»",
                        value=settings.notifications.show_recording_notification,
                        on_change=_bool_handler(
                            settings, prefs, "notifications.show_recording_notification"
                        ),
                    ),
                    ft.Switch(
                        label="Предупреждать о потере GPS",
                        value=settings.notifications.warn_gps_lost,
                        on_change=_bool_handler(settings, prefs, "notifications.warn_gps_lost"),
                    ),
                    ft.Switch(
                        label="Предупреждать о сходе с маршрута",
                        value=settings.notifications.warn_route_deviation,
                        on_change=_bool_handler(
                            settings, prefs, "notifications.warn_route_deviation"
                        ),
                    ),
                    ft.Dropdown(
                        label="Порог схода с маршрута",
                        value=str(settings.notifications.route_deviation_threshold_m),
                        options=[
                            ft.dropdown.Option(str(v), f"{v} м") for v in (50, 100, 200, 500)
                        ],
                        on_select=_int_handler(
                            settings, prefs, "notifications.route_deviation_threshold_m"
                        ),
                    ),
                    ft.Dropdown(
                        label="Порог низкого заряда батареи",
                        value=str(settings.notifications.low_battery_threshold),
                        options=[
                            ft.dropdown.Option(str(v), f"{v} %") for v in (10, 15, 20, 25)
                        ],
                        on_select=_int_handler(
                            settings, prefs, "notifications.low_battery_threshold"
                        ),
                    ),
                ], spacing=12),
            ),
        ],
    )

    # =============== Единицы измерения ===============
    units_section = ft.ExpansionTile(
        title=ft.Text("Единицы измерения"),
        subtitle=ft.Text("Расстояние, скорость, координаты"),
        leading=ft.Icon(ft.Icons.STRAIGHTEN),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Dropdown(
                        label="Расстояние",
                        value=settings.units.distance.value,
                        options=[
                            ft.dropdown.Option(DistanceUnit.KM.value, "Километры"),
                            ft.dropdown.Option(DistanceUnit.MILES.value, "Мили"),
                        ],
                        on_select=_enum_handler(settings, prefs, "units.distance", DistanceUnit),
                    ),
                    ft.Dropdown(
                        label="Скорость",
                        value=settings.units.speed.value,
                        options=[
                            ft.dropdown.Option(SpeedUnit.KMH.value, "км/ч"),
                            ft.dropdown.Option(SpeedUnit.MPH.value, "миль/ч"),
                        ],
                        on_select=_enum_handler(settings, prefs, "units.speed", SpeedUnit),
                    ),
                    ft.Dropdown(
                        label="Высота",
                        value=settings.units.altitude.value,
                        options=[
                            ft.dropdown.Option(AltitudeUnit.METERS.value, "Метры"),
                            ft.dropdown.Option(AltitudeUnit.FEET.value, "Футы"),
                        ],
                        on_select=_enum_handler(settings, prefs, "units.altitude", AltitudeUnit),
                    ),
                    ft.Dropdown(
                        label="Формат координат",
                        value=settings.units.coordinates.value,
                        options=[
                            ft.dropdown.Option(CoordFormat.DD.value, "55.751244 (DD)"),
                            ft.dropdown.Option(CoordFormat.DMS.value, "55°45'04\"N (DMS)"),
                        ],
                        on_select=_enum_handler(
                            settings, prefs, "units.coordinates", CoordFormat
                        ),
                    ),
                ], spacing=12),
            ),
        ],
    )

    # =============== Отображение ===============
    async def theme_changed(e):
        try:
            settings.display.theme = ThemeMode(e.control.value)
        except (ValueError, TypeError):
            return
        apply_theme(page, settings)
        await save_settings(prefs, settings)
        page.update()

    display_section = ft.ExpansionTile(
        title=ft.Text("Отображение"),
        subtitle=ft.Text("Тема, шрифт, слои на карте"),
        leading=ft.Icon(ft.Icons.PALETTE),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Dropdown(
                        label="Тема",
                        value=settings.display.theme.value,
                        options=[
                            ft.dropdown.Option(ThemeMode.LIGHT.value, "Светлая"),
                            ft.dropdown.Option(ThemeMode.DARK.value, "Тёмная"),
                            ft.dropdown.Option(ThemeMode.SYSTEM.value, "Системная"),
                        ],
                        on_select=theme_changed,
                    ),
                    ft.Switch(
                        label="Крупный шрифт (удобно в поле)",
                        value=settings.display.large_font,
                        on_change=_bool_handler(settings, prefs, "display.large_font"),
                    ),
                    ft.Switch(
                        label="Показывать записанный трек",
                        value=settings.display.show_track_on_map,
                        on_change=_bool_handler(settings, prefs, "display.show_track_on_map"),
                    ),
                    ft.Switch(
                        label="Показывать активный маршрут",
                        value=settings.display.show_route_on_map,
                        on_change=_bool_handler(settings, prefs, "display.show_route_on_map"),
                    ),
                    ft.Switch(
                        label="Показывать путевые точки",
                        value=settings.display.show_waypoints,
                        on_change=_bool_handler(settings, prefs, "display.show_waypoints"),
                    ),
                ], spacing=12),
            ),
        ],
    )

    # =============== Данные ===============
    def confirm_reset(e):
        async def on_confirm(ev):
            page.close(dialog)
            fresh = AppSettings()
            for sec in ("gps", "maps", "sync", "notifications", "units", "display", "data"):
                setattr(settings, sec, getattr(fresh, sec))
            await save_settings(prefs, settings)
            apply_theme(page, settings)
            rebuild()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Сбросить все настройки?"),
            content=ft.Text("Параметры вернутся к заводским. Треки и маршруты останутся."),
            actions=[
                ft.TextButton("Отмена", on_click=lambda _: page.close(dialog)),
                ft.FilledButton(
                    "Сбросить",
                    on_click=on_confirm,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED),
                ),
            ],
        )
        page.open(dialog)

    data_section = ft.ExpansionTile(
        title=ft.Text("Данные и хранилище"),
        subtitle=ft.Text("Автоудаление, аналитика, сброс"),
        leading=ft.Icon(ft.Icons.STORAGE),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Dropdown(
                        label="Автоудаление старых треков",
                        value=settings.data.auto_delete_old_tracks.value,
                        options=[
                            ft.dropdown.Option(AutoDeletePolicy.NEVER.value, "Никогда"),
                            ft.dropdown.Option(
                                AutoDeletePolicy.SIX_MONTHS.value, "Старше 6 месяцев"
                            ),
                            ft.dropdown.Option(AutoDeletePolicy.ONE_YEAR.value, "Старше года"),
                        ],
                        on_select=_enum_handler(
                            settings, prefs,
                            "data.auto_delete_old_tracks", AutoDeletePolicy,
                        ),
                    ),
                    ft.Switch(
                        label="Собирать анонимную статистику",
                        value=settings.data.analytics_enabled,
                        on_change=_bool_handler(settings, prefs, "data.analytics_enabled"),
                    ),
                    ft.FilledButton(
                        "Сбросить настройки к заводским",
                        icon=ft.Icons.RESTART_ALT,
                        on_click=confirm_reset,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700),
                    ),
                ], spacing=12),
            ),
        ],
    )

    # =============== О приложении ===============
    about_section = ft.ExpansionTile(
        title=ft.Text("О приложении"),
        subtitle=ft.Text("Версия 1.0.0"),
        leading=ft.Icon(ft.Icons.INFO_OUTLINE),
        controls=[
            ft.Container(
                padding=ft.Padding(16, 12, 16, 12),
                content=ft.Column([
                    ft.Text("GPS Трекер · v1.0.0", weight=ft.FontWeight.BOLD),
                    ft.Text(
                        "Приложение для записи треков и планирования маршрутов.",
                        size=12,
                    ),
                    ft.TextButton(
                        "Связаться с разработчиком",
                        icon=ft.Icons.EMAIL,
                        url="mailto:dev@example.com",
                    ),
                ], spacing=8),
            ),
        ],
    )

    # =============== Собираем View ===============
    return ft.Column(
        expand=True,
        controls=[
            ft.ListView(
                expand=True,
                spacing=8,
                padding=10,
                controls=[
                    gps_section, maps_section, sync_section,
                    notifications_section, units_section, display_section,
                    data_section, about_section,
                ],
            ),
        ],
        spacing=0,
    )