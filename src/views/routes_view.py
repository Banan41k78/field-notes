"""Контент вкладки «Маршруты»."""
import flet as ft

from app_context import AppContext


def build_routes_content(ctx: AppContext) -> ft.Control:
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(ft.Icons.LIST_ALT_OUTLINED, size=64, color=ft.Colors.GREY),
                ft.Text("Здесь будут сохранённые маршруты", size=20),
                ft.Text(
                    "Импортируйте GPX/KML или создайте маршрут на десктопе.",
                    size=12,
                    color=ft.Colors.GREY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )