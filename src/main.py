"""Точка входа с PageView, AppBar, NavigationBar и обработкой выхода."""
import asyncio

import flet as ft

from app_context import AppContext
from config import load_settings
from views.map_view import build_map_content
from views.tracks_view import build_tracks_content
from views.routes_view import build_routes_content
from views.settings_views import build_settings_content, apply_theme


# Названия и иконки для AppBar и NavigationBar
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

    # 2. Флаг-блокировка on_change на время «дальнего» перехода
    is_jumping = False

    # 3. PageView со всеми вкладками
    #    implicit_scrolling=False — не рендерим соседние страницы заранее,
    #    это убирает «мелькание» при прыжках через несколько вкладок.
    page_view = ft.PageView(
        expand=True,
        horizontal=True,
        implicit_scrolling=False,
        controls=[
            build_map_content(ctx),
            build_tracks_content(ctx),
            build_routes_content(ctx),
            build_settings_content(ctx),
        ],
        on_change=lambda e: sync_ui(int(e.data)),
    )

    # 4. Синхронизация AppBar и NavigationBar
    def sync_ui(index: int):
        # Пока идёт «дальний» прыжок — не трогаем UI, чтобы не вызвать лишнюю перерисовку
        if is_jumping:
            return
        page.navigation_bar.selected_index = index
        page.appbar.title.value = TAB_TITLES[index]
        page.update()

    # 5. Обработчик переключения вкладки через NavigationBar
    async def on_nav_change(e):
        nonlocal is_jumping
        idx = e.control.selected_index
        current = page_view.selected_index
        if idx == current:
            return

        distance = abs(idx - current)

        if distance > 1:
            # --- ДАЛЬНИЙ ПЕРЕХОД: без анимации, без промежуточных страниц ---
            is_jumping = True

            # Мгновенно перемещаем «ползунок» в целевую позицию
            page_view.selected_index = idx
            page_view.update()

            # Обновляем только NavigationBar и AppBar
            page.navigation_bar.selected_index = idx
            page.appbar.title.value = TAB_TITLES[idx]
            page.update()

            # Снимаем блокировку
            is_jumping = False
        else:
            # --- СОСЕДНИЙ ПЕРЕХОД: плавный слайд ---
            await page_view.go_to_page(
                idx,
                animation_duration=ft.Duration(milliseconds=250),
                animation_curve=ft.AnimationCurve.EASE_IN_OUT,
            )

    # 6. AppBar и NavigationBar на уровне Page
    page.appbar = ft.AppBar(title=ft.Text(TAB_TITLES[0]))
    page.navigation_bar = ft.NavigationBar(
        selected_index=0,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(icon=TAB_ICONS[i], label=TAB_TITLES[i])
            for i in range(4)
        ],
    )

    # 7. Обработка системной кнопки «Назад»
    async def view_pop(e):
        if len(page.views) <= 1:
            await show_exit_dialog(page)
            return
        page.views.remove(e.view)
        page.update()

    page.on_view_pop = view_pop

    # 8. Добавляем PageView на страницу
    page.add(page_view)


async def show_exit_dialog(page: ft.Page):
    """Диалог подтверждения выхода из приложения."""
    def close_app(e):
        page.window.destroy()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Выйти из приложения?"),
        content=ft.Text("Текущие данные сохранены."),
        actions=[
            ft.TextButton("Отмена", on_click=lambda _: page.close(dialog)),
            ft.FilledButton(
                "Выйти",
                on_click=close_app,
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED),
            ),
        ],
    )
    page.open(dialog)


ft.run(main)