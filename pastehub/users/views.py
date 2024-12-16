from datetime import timedelta

import django.conf
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from paste.models import Paste
import users.forms
import users.models


def signup(request):
    form = users.forms.SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_active = django.conf.settings.DEFAULT_USER_IS_ACTIVE
        user.save()

        if not user.is_active:
            token = get_random_string(length=32)

            user.confirmation_token = token
            user.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            activate_url = request.build_absolute_uri(
                reverse(
                    "auth:activate",
                    kwargs={"uidb64": uid, "token": token},
                ),
            )

            send_mail(
                subject="Активация аккаунта",
                message=activate_url,
                html_message=f'<a href="{activate_url}">{activate_url}</a>',
                from_email=django.conf.settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )

            return render(
                request,
                "auth/activation_sent.html",
                {"title": "Активация аккаунта", "user": user},
            )

    return render(request, "auth/signup.html", {"form": form})


def activate(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = get_object_or_404(users.models.CustomUser, pk=uid)

    if (
        user.confirmation_token == token
        and user.date_joined + timedelta(hours=12) > timezone.now()
    ):
        user.is_active = True
        user.confirmation_token = None
        user.save()

        return render(
            request,
            "auth/activation_success.html",
            {"title": "Успешная активация"},
        )

    return render(
        request,
        "auth/activation_expired.html",
        {"title": "Ссылка просрочена"},
    )


def user_detail(request, username):
    user = get_object_or_404(users.models.CustomUser, username=username)

    user_pastes = (
        user.pastes.select_related("category")
        .only(
            Paste.title.field.name,
            Paste.created.field.name,
            Paste.category.field.name,
            Paste.author.field.name,
        )
        .all()
    )

    return render(
        request,
        "users/user_detail.html",
        {"pastes": user_pastes, "user": user},
    )


@login_required
def profile_edit(request):
    user = request.user
    profile_form = users.forms.ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
    )

    if request.method == "POST" and profile_form.is_valid():
        profile_form.save()
        messages.success(request, "Профиль успешно сохранён")

    return render(
        request,
        "users/profile.html",
        {"form": profile_form, "user": user},
    )


__all__ = ()
