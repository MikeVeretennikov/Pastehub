import os
import re

from django.shortcuts import get_object_or_404, redirect, render

from core.crypto import AESEncryption
from core.storage import (
    delete_from_storage,
    get_from_storage,
    upload_to_storage,
)
from paste.forms import GetPasswordForm, PasteForm, ProtectedPasteForm
from paste.models import Paste, PasteVersion, ProtectedPaste


def create(request):

    form = PasteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        instance = form.save(commit=False)

        if request.user.is_authenticated:
            instance.author = request.user

        content = form.cleaned_data.get("content")
        clear_content = content.replace("\r\n", "\n").strip()

        uploaded = upload_to_storage(f"pastes/{instance.id}", clear_content)

        if uploaded:
            instance.save()
            upload_to_storage(f"pastes_version/{instance.id}_1", clear_content)

        return redirect("paste:detail", short_link=instance.short_link)

    return render(
        request=request,
        template_name="paste/create.html",
        context={"form": form},
    )


def edit(request, short_link):
    paste = get_object_or_404(Paste, short_link=short_link)
    content = get_from_storage(f"pastes/{paste.id}")

    form = PasteForm(
        request.POST or None,
        instance=paste,
        initial={"content": content},
    )

    if form.is_valid() and request.POST:
        content = form.cleaned_data.get("content")
        clear_content = content.replace("\r\n", "\n").strip()

        last_version = (
            PasteVersion.objects.filter(paste=paste)
            .order_by("-updated")
            .first()
        )

        new_verison = last_version.version + 1
        upload_to_storage(
            f"pastes_version/{paste.id}_{new_verison}",
            content,
        )
        delete_from_storage(f"pastes/{paste.id}")
        upload_to_storage(f"pastes/{paste.id}", clear_content)

        form.save()

        return redirect(
            "paste:version-detail",
            short_link=short_link,
            version=new_verison,
        )

    return render(
        request=request,
        template_name="paste/create.html",
        context={"form": form, "is_edit_page": True},
    )


def detail(request, short_link, version=None):
    paste = get_object_or_404(Paste, short_link=short_link)
    paste_uuid = paste.id

    if version:
        old_paste = (
            PasteVersion.objects.filter(paste=paste)
            .order_by("-updated")
            .first()
        )
        content = get_from_storage(f"pastes_version/{paste_uuid}_{version}")

        return render(
            request=request,
            template_name="paste/detail.html",
            context={
                "paste": paste,
                "old_paste": old_paste,
                "content": content,
                "version": version,
            },
        )

    content = get_from_storage(f"pastes/{paste.id}")

    return render(
        request=request,
        template_name="paste/detail.html",
        context={"paste": paste, "content": content, "version": 1},
    )


def delete(request, short_link):
    paste = get_object_or_404(Paste, short_link=short_link)

    if request.user != paste.author:
        return redirect("paste:detail", short_link=short_link)

    delete_from_storage(f"pastes/{paste.id}")

    directory = "media/pastes_version/"
    regex = re.compile(f"{paste.id}_?[0-9]+")

    for filename in os.listdir(directory):
        if regex.match(filename):
            print(filename)
            delete_from_storage(f"pastes_version/{filename}")

    paste.delete()

    return redirect("paste:create")


def create_protected(request):
    form = ProtectedPasteForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        instance = form.save(commit=False)

        if request.user.is_authenticated:
            instance.author = request.user

        content = form.cleaned_data.get("content")
        clear_content = content.replace("\r\n", "\n").strip()

        password = form.cleaned_data.get("password")

        salt, nonce, ciphertext = AESEncryption.encrypt(
            password=password,
            text=clear_content,
        )
        instance.set_password(password)
        instance.salt = salt
        instance.nonce = nonce

        uploaded = upload_to_storage(f"pastes/{instance.id}", ciphertext)
        if uploaded:
            instance.save()

        return redirect(
            "paste:detail_protected",
            short_link=instance.short_link,
        )

    return render(
        request=request,
        template_name="paste/create_protected.html",
        context={"form": form},
    )


def detail_protected(request, short_link):
    paste = get_object_or_404(ProtectedPaste, short_link=short_link)
    encrypted_content = get_from_storage(f"pastes/{paste.id}")

    form = GetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data.get("password")
        if not paste.check_password(password):
            return redirect("paste:create_protected")

        decrypted_content = AESEncryption.decrypt(
            password=password,
            salt=paste.salt,
            nonce=paste.nonce,
            ciphertext=encrypted_content,
        )

        return render(
            request=request,
            template_name="paste/detail_protected.html",
            context={"paste": paste, "content": decrypted_content},
        )

    return render(
        request=request,
        template_name="paste/get_password.html",
        context={"form": form},
    )


def delete_protected(request, short_link):
    paste = get_object_or_404(ProtectedPaste, short_link=short_link)
    form = GetPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data.get("password")
        if not paste.check_password(password):
            return redirect("paste:create")

        delete_from_storage(f"pastes/{paste.id}")
        paste.delete()

        return redirect("paste:create_protected")

    return render(
        request=request,
        template_name="paste/get_password.html",
        context={"form": form},
    )


__all__ = []
