from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render

from core.crypto import AESEncryption
from core.storage import (
    delete_from_storage,
    get_from_storage,
    upload_to_storage,
)
from core.utils import search_in_file
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
            PasteVersion.objects.create(
                paste=instance,
                version=1,
                title=instance.title,
                short_link=instance.short_link,
            )
            upload_to_storage(
                f"pastes/versions/{instance.id}_1",
                clear_content,
            )

        return redirect("paste:detail", short_link=instance.short_link)

    return render(
        request=request,
        template_name="paste/create.html",
        context={"form": form},
    )


def edit(request, short_link):
    paste = get_object_or_404(Paste, short_link=short_link)
    paste_title = paste.title
    content = get_from_storage(f"pastes/{paste.id}")

    form = PasteForm(
        request.POST or None,
        instance=paste,
        initial={"content": content},
    )

    if form.is_valid() and request.POST:
        form_title = form.cleaned_data.get("title")
        form_content = form.cleaned_data.get("content")
        clear_content = form_content.replace("\r\n", "\n").strip()

        if clear_content != content or paste_title != form_title:
            last_version = (
                PasteVersion.objects.filter(paste=paste)
                .order_by("-updated")
                .first()
            )
            new_version = last_version.version + 1
            PasteVersion.objects.create(
                paste=paste,
                version=new_version,
                title=form_title,
                short_link=paste.short_link,
            )
            upload_to_storage(
                f"pastes/versions/{paste.id}_{new_version}",
                clear_content,
            )
            delete_from_storage(f"pastes/{paste.id}")
            upload_to_storage(f"pastes/{paste.id}", clear_content)

        form.save()

        return redirect(
            "paste:detail",
            short_link=short_link,
        )

    return render(
        request=request,
        template_name="paste/create.html",
        context={"form": form, "is_edit_page": True},
    )


def detail(request, short_link, version=None):
    paste = get_object_or_404(Paste, short_link=short_link)
    content = get_from_storage(f"pastes/{paste.id}")
    selected_version = (
        PasteVersion.objects.filter(paste=paste).order_by("-updated").first()
    )
    old_version = selected_version.version

    if paste.is_blocked and request.user != paste.author:
        return render(
            request=request,
            template_name="paste/blocked.html",
        )

    if version:
        if version == selected_version.version:
            return redirect("paste:detail", short_link=short_link)

        selected_version = get_object_or_404(
            PasteVersion,
            version=version,
            paste=paste,
        )
        content = get_from_storage(f"pastes/versions/{paste.id}_{version}")

        return render(
            request=request,
            template_name="paste/detail.html",
            context={
                "paste": paste,
                "old_version": old_version,
                "content": content,
                "selected_version": selected_version,
            },
        )

    return render(
        request=request,
        template_name="paste/detail.html",
        context={
            "paste": paste,
            "content": content,
            "selected_version": selected_version,
            "old_version": old_version,
        },
    )


def delete(request, short_link):
    paste = get_object_or_404(Paste, short_link=short_link)

    if request.user != paste.author:
        return redirect("paste:detail", short_link=short_link)

    delete_from_storage(f"pastes/{paste.id}")

    count_versions = PasteVersion.objects.filter(paste=paste).count()
    for i in range(1, count_versions + 1):
        delete_from_storage(f"pastes/versions/{paste.id}_{i}")

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


def search(request):
    query = request.GET.get("q", "").strip()

    page = request.GET.get("page")
    if not str(page).isdigit():
        return HttpResponseBadRequest("Page is not integer")

    page = int(page)

    directory = "pastes/"
    if query and default_storage.exists(directory):
        pastes_list = []

        directories, files = default_storage.listdir(directory)

        for id_paste in files:
            file_path = f"{directory}{id_paste}"
            if default_storage.exists(file_path):
                if search_in_file(file_path, query):
                    pastes_list.append(id_paste)

        object_list = (
            Paste.objects.all()
            .filter(
                Q(title__icontains=query)
                | Q(category__name__icontains=query)
                | Q(id__in=pastes_list),
                is_published=True,
            )
            .prefetch_related(Paste.category.field.name)
        )
        order_by_object_list = object_list.order_by(Paste.created.field.name)
        limited_object_list = order_by_object_list.only(
            Paste.title.field.name,
            Paste.created.field.name,
            Paste.category.field.name,
            Paste.author.field.name,
        )
    else:
        limited_object_list = []

    paginator = Paginator(limited_object_list, 25)
    page_obj = paginator.get_page(page)
    return render(
        request=request,
        template_name="paste/search_results.html",
        context={
            "query": query,
            "list_pages": list(paginator.page_range),
            "page_obj": page_obj,
        },
    )


__all__ = []
