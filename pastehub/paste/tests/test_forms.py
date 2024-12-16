import os
import shutil

from django.conf import settings
from django.test import override_settings, TestCase
from django.urls import reverse

from paste.models import Category, Paste


@override_settings(
    MEDIA_ROOT=settings.BASE_DIR / "media_test",
)
class TestForms(TestCase):
    def setUp(self):
        Category.objects.create(name="Test Category")

    def tearDown(self):
        Paste.objects.all().delete()
        Category.objects.all().delete()

        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def test_create_forms(self):
        pastes_count = Paste.objects.count()

        data = {
            "title": "Test title",
            "content": "Test content",
            "category": 1,
            "language": "text",
        }

        response = self.client.post(
            reverse("paste:create"),
            data,
            follow=True,
        )

        self.assertEqual(Paste.objects.count(), pastes_count + 1)
        self.assertIn("messages", response.context)

    def test_create_forms_errors(self):
        data = {
            "title": "",
            "content": "",
            "category": "Non",
        }

        response = self.client.post(
            reverse("paste:create"),
            data,
            follow=True,
        )

        self.assertTrue(response.context["form"].has_error("title"))
        self.assertTrue(response.context["form"].has_error("content"))
        self.assertTrue(response.context["form"].has_error("category"))


__all__ = []
