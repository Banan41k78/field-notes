# Field Notes

**Offline-first GPS tracker and route planner for hiking, cycling, and driving.**
Written entirely in Python with [Flet](https://flet.dev) — one codebase for Android,
desktop, and web.

> Записывайте треки в поле без интернета → синхронизируйте с десктопом → получайте
> подробные отчёты с метриками, профилем высот и экспортом в GPX/KML.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.28+-purple.svg)](https://flet.dev)

---

## Возможности

-  **Интерактивная карта** — OSM, Яндекс, спутник (Esri), топографическая подложка
-  **Запись GPS-трека** — старт, пауза, продолжение, стоп
-  **Статистика в реальном времени** — расстояние, скорость, длительность
-  **Офлайн-first** — треки сохраняются локально, работают без сети
-  **Экспорт/импорт GPX** — совместимость с Garmin, Organic Maps, Strava
-  **Гибкие настройки** — точность GPS, частота записи, единицы измерения, тема

##  Статус

MVP в активной разработке. Готово: каркас приложения (4 вкладки), экран настроек,
запись трека, карта с текущей позицией, хранилище треков и маршрутов.

В работе: список треков, детальный экран, навигация по маршруту, синхронизация.

##  Технологии

| Слой | Стек |
|---|---|
| **UI** | Flet 0.28+ (Material Design 3) |
| **Карты** | `flet-map` (flutter_map) |
| **Геолокация** | `flet-geolocator` |
| **Хранение** | JSON в `FLET_APP_STORAGE_DATA` |
| **Форматы** | `gpxpy`, `fastkml` |
| **Python** | 3.12+ |

## 📂 Структура проекта
```
field-notes/
├── src/
│ ├── main.py # Точка входа, PageView, навигация
│ ├── app_context.py # AppContext + AppServices
│ ├── config.py # AppSettings, apply_theme, load/save
│ ├── models/ # Track, Route, TrackPoint, RoutePoint
│ ├── services/ # location, track_recorder, storage, gpx_parser
│ ├── components/ # gps_status_bar, stat_bar, record_controls
│ └── views/ # map_view, tracks_view, routes_view, settings_views
├── assets/
│ └── icon.png
├── pyproject.toml
├── requirements.txt
└── README.md
```
