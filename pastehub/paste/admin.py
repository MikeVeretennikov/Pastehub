from django.contrib import admin

from core.storage import delete_from_storage
from paste.models import Category, Paste, PasteVersion, ProtectedPaste


class VersionsInline(admin.TabularInline):
    model = PasteVersion
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Paste)
class PasteAdmin(admin.ModelAdmin):
    list_display = [
        Paste.id.field.name,
        Paste.title.field.name,
        Paste.category.field.name,
        Paste.created.field.name,
    ]

    list_filter = [
        Paste.category.field.name,
        Paste.created.field.name,
    ]

    readonly_fields = [
        Paste.author.field.name,
    ]

    inlines = [VersionsInline]

    def delete_model(self, request, obj):
        delete_from_storage(f"pastes/{obj.pk}")
        super().delete_model(request, obj)


@admin.register(ProtectedPaste)
class ProtectedPasteAdmin(admin.ModelAdmin):
    list_display = [
        ProtectedPaste.id.field.name,
        ProtectedPaste.title.field.name,
        ProtectedPaste.created.field.name,
    ]

    list_filter = [
        ProtectedPaste.created.field.name,
    ]

    readonly_fields = [
        ProtectedPaste.password.field.name,
    ]

    def delete_model(self, request, obj):
        delete_from_storage(f"pastes/{obj.pk}")
        super().delete_model(request, obj)


@admin.register(PasteVersion)
class PasteVersionAdmin(admin.ModelAdmin):
    readonly_fields = [
        PasteVersion.paste.field.name,
    ]

    def delete_model(self, request, obj):
        delete_from_storage(f"pastes/versions/{obj.paste.pk}_{obj.pk}")
        super().delete_model(request, obj)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


__all__ = []
