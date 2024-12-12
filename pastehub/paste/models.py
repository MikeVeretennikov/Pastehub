from datetime import timedelta
import uuid

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone

from core.utils import generate_short_link


class Category(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="категория",
        help_text="Максимальная длинна 150 символов",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class BasePasteModel(models.Model):
    EXPIRED_LIMIT = [
        (None, "Бессрочно"),
        (timedelta(minutes=10), "10 минут"),
        (timedelta(hours=1), "1 час"),
        (timedelta(days=1), "1 день"),
        (timedelta(days=5), "5 дней"),
        (timedelta(days=10), "10 дней"),
        (timedelta(days=30), "30 дней"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=150,
        verbose_name="заголовок",
        help_text="Максимальная длинна 150 символов",
    )
    short_link = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="короткая ссылка",
    )
    expired_duration = models.DurationField(
        choices=EXPIRED_LIMIT,
        default=None,
        null=True,
        blank=True,
        verbose_name="срок существования пасты",
    )
    expired_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="дата уничтожения пасты",
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="создана")

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = generate_short_link()

        if self.expired_duration:
            self.expired_date = timezone.now() + self.expired_duration

        super().save(*args, **kwargs)


class Paste(BasePasteModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="pastes",
        related_query_name="paste",
        verbose_name="категория",
        null=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="pastes",
        related_query_name="paste",
        verbose_name="автор",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="опубликовать",
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="заблокировать",
    )
    updated = models.DateTimeField(auto_now=True, verbose_name="обновлён")

    class Meta:
        verbose_name = "паста"
        verbose_name_plural = "пасты"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            last_version = (
                PasteVersion.objects.filter(paste=self)
                .order_by("-updated")
                .first()
            )
            next_version = last_version.version + 1 if last_version else 1
        else:
            next_version = 1

        if not self.short_link:
            self.short_link = generate_short_link()

        super().save(*args, **kwargs)

        PasteVersion.objects.create(
            paste=self,
            version=next_version,
            title=self.title,
            short_link=self.short_link,
        )


class PasteVersion(models.Model):
    paste = models.ForeignKey(
        Paste,
        on_delete=models.CASCADE,
        verbose_name="паста",
        related_name="versions",
    )
    version = models.IntegerField(verbose_name="номер версии")
    title = models.CharField(
        max_length=150,
        verbose_name="заголовок",
        help_text="Максимальная длинна 150 символов",
    )
    short_link = models.CharField(
        max_length=10,
        unique=False,
        verbose_name="короткая ссылка",
    )
    updated = models.DateTimeField(auto_now=True, verbose_name="обновлён")

    class Meta:
        verbose_name = "версия пасты"
        verbose_name_plural = "версии паст"

    def __str__(self):
        return f"{self.paste.title} - Версия {self.version}"


class ProtectedPaste(BasePasteModel):
    password = models.CharField(max_length=255, verbose_name="ключ шифрования")
    salt = models.BinaryField(verbose_name="соль")
    nonce = models.BinaryField(verbose_name="nonce")

    class Meta:
        verbose_name = "зашифрованная паста"
        verbose_name_plural = "зашифрованные пасты"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


__all__ = ["Category", "Paste", "ProtectedPaste"]
