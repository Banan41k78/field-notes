"""Заглушка вкладки «Треки»."""
import flet as ft

from app_context import AppContext
from views._nav import build_nav_bar


def build_tracks_view(ctx: AppContext) -> ft.View:
    return ft.View(
        route="/tracks",
        appbar=ft.AppBar(title=ft.Text("Треки")),
        padding=0,
        controls=[
            ft.Column([
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.Alignment.CENTER,
                    content=ft.Text("Здесь будут записанные треки", size=20),
                ),
                build_nav_bar(1, ctx.page),
            ], expand=True, spacing=0),
        ],
    )