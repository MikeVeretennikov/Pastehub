import http
import shutil

from django.conf import settings
from django.test import override_settings, TestCase
from django.urls import reverse

from core.storage import upload_to_storage
from paste.models import Paste


@override_settings(
    MEDIA_ROOT=settings.BASE_DIR / "media_test",
)
class TestViews(TestCase):
    def setUp(self):
        self.test_paste = Paste.objects.create(
            title="Test Paste",
            is_published=True,
        )
        upload_to_storage(
            f"pastes/{self.test_paste.id}",
            "Lorem ipsum dolor sit amet...",
        )

    def tearDown(self):
        Paste.objects.all().delete()
        shutil.rmtree(settings.MEDIA_ROOT)

    def test_search_positive(self):
        response = self.client.get(
            f'{reverse("paste:search")}?q=ipsum&page=1',
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(
            response.context["page_obj"].object_list[0].title,
            "Test Paste",
        )

    def test_search_word_not_in_pastes_negative(self):
        response = self.client.get(
            f'{reverse("paste:search")}?q=wordnotinpastes&page=1',
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(
            len(response.context["page_obj"].object_list),
            0,
        )

    def test_search_pages_not_integer_negative(self):
        response = self.client.get(
            f'{reverse("paste:search")}?q=wordnotinpastes&page=1.5',
        )
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)


__all__ = []
