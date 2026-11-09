"""Заглушка вкладки «Маршруты»."""
import flet as ft

from app_context import AppContext
from views._nav import build_nav_bar


def build_routes_view(ctx: AppContext) -> ft.View:
    return ft.View(
        route="/routes",
        appbar=ft.AppBar(title=ft.Text("Маршруты")),
        padding=0,
        controls=[
            ft.Column([
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Text("Здесь будут сохранённые маршруты", size=20),
                ),
                build_nav_bar(2, ctx.page),
            ], expand=True, spacing=0),
        ],
    )