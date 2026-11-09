"""Общая нижняя навигация для всех вкладок."""
import flet as ft

TAB_ROUTES = ["/", "/tracks", "/routes", "/settings"]
TAB_LABELS = ["Карта", "Треки", "Маршруты", "Настройки"]
TAB_ICONS = [ft.Icons.MAP, ft.Icons.ROUTE, ft.Icons.LIST, ft.Icons.SETTINGS]


def build_nav_bar(current_index: int, page: ft.Page) -> ft.NavigationBar:
    async def on_change(e):
        idx = e.control.selected_index
        if idx == current_index:
            return
        await page.push_route(TAB_ROUTES[idx])

    return ft.NavigationBar(
        selected_index=current_index,
        on_change=on_change,
        destinations=[
            ft.NavigationBarDestination(icon=TAB_ICONS[i], label=TAB_LABELS[i])
            for i in range(4)
        ],
    )