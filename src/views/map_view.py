"""Заглушка вкладки «Карта»."""
import flet as ft

from app_context import AppContext
from views._nav import build_nav_bar


def build_map_view(ctx: AppContext) -> ft.View:
    return ft.View(
        route="/",
        appbar=ft.AppBar(title=ft.Text("Карта")),
        padding=0,
        controls=[
            ft.Column([
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Text("Здесь будет карта", size=20),
                ),
                build_nav_bar(0, ctx.page),
            ], expand=True, spacing=0),
        ],
    )