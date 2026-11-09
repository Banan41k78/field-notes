"""Контент вкладки «Треки»."""
import flet as ft

from app_context import AppContext


def build_tracks_content(ctx: AppContext) -> ft.Control:
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(ft.Icons.ROUTE_OUTLINED, size=64, color=ft.Colors.GREY),
                ft.Text("Здесь будут записанные треки", size=20),
                ft.Text(
                    "Пока ничего не записано.\nНачните запись на вкладке «Карта».",
                    size=12,
                    color=ft.Colors.GREY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )