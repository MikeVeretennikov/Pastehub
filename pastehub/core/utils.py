import mmap
import random
import string

from django.conf import settings


def generate_short_link(length=settings.SHORT_LINK_LENGTH):
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=length),
    )


def search_in_file(file_path, search_term):
    with open(file_path, "r+b") as f:
        mmapped_file = mmap.mmap(f.fileno(), 0)
        search_term_bytes = search_term.encode("utf-8")
        return mmapped_file.find(search_term_bytes) != -1


__all__ = ["generate_short_link"]
