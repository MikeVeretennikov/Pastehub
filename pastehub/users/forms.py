from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserChangeForm,
    UserCreationForm,
)

from core.forms import BootstrapFormMixin
import users.models


class SignUpForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = users.models.CustomUser
        fields = (
            model.email.field.name,
            model.username.field.name,
            "password1",
            "password2",
        )

        help_texts = {
            model.email.field.name: "Введите вашу почту",
            model.username.field.name: "Введите имя пользователя",
        }


class ProfileForm(BootstrapFormMixin, UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = users.models.CustomUser
        fields = (
            model.email.field.name,
            model.username.field.name,
            model.image.field.name,
        )

        widgets = {model.image.field.name: forms.ClearableFileInput()}


class BootstrapPasswordChangeForm(BootstrapFormMixin, PasswordChangeForm):
    pass


class BootstrapAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    pass


class BootstrapPasswordResetForm(BootstrapFormMixin, PasswordResetForm):
    pass


class BootstrapSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass


__all__ = ()
