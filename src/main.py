"""Точка входа"""
import flet as ft

from app_context import AppContext
from config import load_settings
from views.map_view import build_map_content
from views.tracks_view import build_tracks_content
from views.routes_view import build_routes_content
from views.settings_views import build_settings_content, apply_theme


# Метаданные вкладок для AppBar и NavigationBar
TAB_TITLES = ["Карта", "Треки", "Маршруты", "Настройки"]
TAB_ICONS = [ft.Icons.MAP, ft.Icons.ROUTE, ft.Icons.LIST, ft.Icons.SETTINGS]


async def main(page: ft.Page):
    page.title = "Field Notes"

    # 1. Инициализация контекста
    prefs = ft.SharedPreferences()
    page.services.append(prefs)
    settings = await load_settings(prefs)
    apply_theme(page, settings)
    ctx = AppContext(page=page, prefs=prefs, settings=settings)

    # 2. Создаём PageView с контентом всех вкладок
    #    Каждая функция build_*_content возвращает НЕ View, а Column/Container
    page_view = ft.PageView(
        expand=True,
        horizontal=True,
        controls=[
            build_map_content(ctx),
            build_tracks_content(ctx),
            build_routes_content(ctx),
            build_settings_content(ctx),
        ],
        on_change=lambda e: sync_nav_bar(int(e.data)),
    )

    # 3. Функция синхронизации NavigationBar с текущей страницей PageView
    def sync_nav_bar(index: int):
        page.navigation_bar.selected_index = index
        page.appbar.title.value = TAB_TITLES[index]
        page.update()

    # 4. Обработчик переключения вкладки через NavigationBar
    async def on_nav_change(e):
        idx = e.control.selected_index
        if idx == page_view.selected_index:
            return
        # go_to_page анимирует переход
        await page_view.go_to_page(idx)
        # on_change PageView вызовется автоматически и обновит AppBar

    # 5. Устанавливаем AppBar и NavigationBar на уровень Page
    page.appbar = ft.AppBar(title=ft.Text(TAB_TITLES[0]))
    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=TAB_ICONS[i], label=TAB_TITLES[i])
            for i in range(4)
        ],
    )

    # 6. Добавляем PageView как единственный контрол на страницу
    #    (можно обернуть в SafeArea, если нужно)
    page.add(page_view)


ft.run(main)