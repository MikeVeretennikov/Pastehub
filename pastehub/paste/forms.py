from django import forms

from core.forms import BootstrapFormMixin
from paste.models import Paste, ProtectedPaste


class PasteForm(BootstrapFormMixin, forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(),
        label="Содержимое",
        help_text="Максимальный объём текста 5 МБ",
        required=True,
    )

    class Meta:
        model = Paste
        fields = [
            model.title.field.name,
            model.category.field.name,
            model.expired_duration.field.name,
            model.is_published.field.name,
            model.language.field.name,
        ]

        widgets = {
            "is_published": forms.CheckboxInput(attrs={"checked": "checked"}),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if content and len(content.encode("utf-8")) > 5 * 1024 * 1024:
            raise forms.ValidationError("Содержимое не должно превышать 5 МБ")

        return content


class ProtectedPasteForm(BootstrapFormMixin, forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(),
        label="Содержимое",
        help_text="Максимальный объём текста 5 МБ",
        required=True,
    )
    password = forms.CharField(
        required=True,
        label="Ключ шифрования",
        widget=forms.PasswordInput(),
    )

    class Meta:
        model = ProtectedPaste
        fields = [
            model.title.field.name,
            model.expired_duration.field.name,
        ]

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if content and len(content.encode("utf-8")) > 5 * 1024 * 1024:
            raise forms.ValidationError("Содержимое не должно превышать 5 МБ")

        return content


class GetPasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Ключ"},
        ),
    )


__all__ = ["GetPasswordForm", "PasteForm", "ProtectedPasteForm"]
