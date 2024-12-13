# Generated by Django 4.2.16 on 2024-12-11 22:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        help_text="Как к вам обращаться?",
                        max_length=150,
                        null=True,
                        verbose_name="имя",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Адрес электронной почты для обратной связи",
                        max_length=254,
                        verbose_name="почта",
                    ),
                ),
            ],
            options={
                "verbose_name": "персональные данные",
                "verbose_name_plural": "персональные данные",
            },
        ),
        migrations.CreateModel(
            name="ReportReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Получено"),
                            ("wip", "В работе"),
                            ("approved", "Принято"),
                            ("rejected", "Отклонено"),
                        ],
                        default="new",
                        max_length=10,
                        verbose_name="статус",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "paste",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="report_review",
                        to="paste.paste",
                        verbose_name="паста",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="report_review",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="автор пасты",
                    ),
                ),
            ],
            options={
                "verbose_name": "пересмотр нарушения",
                "verbose_name_plural": "пересмотры нарушений",
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("new", "Получено"),
                            ("wip", "В работе"),
                            ("approved", "Принято"),
                            ("rejected", "Отклонено"),
                        ],
                        default="new",
                        max_length=10,
                        verbose_name="статус",
                    ),
                ),
                (
                    "text",
                    models.TextField(
                        help_text="Опишите нарушение",
                        verbose_name="текст жалобы",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "paste",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reports",
                        related_query_name="report",
                        to="paste.paste",
                        verbose_name="паста",
                    ),
                ),
                (
                    "person",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="report",
                        to="report.person",
                        verbose_name="отправитель",
                    ),
                ),
            ],
            options={
                "verbose_name": "нарушение",
                "verbose_name_plural": "нарушения",
            },
        ),
    ]
