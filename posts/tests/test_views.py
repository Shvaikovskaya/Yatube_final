import shutil
import time

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.settings as ts
from posts.models import Follow, Group, Post
from posts.settings import PAGE_SIZE

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = ts.TEMP_DIR
        cls.group = Group.objects.create(
            title=ts.GROUP_1_TITLE,
            slug=ts.GROUP_1_SLUG,
            description=ts.GROUP_1_DESCR
        )
        cls.group_2 = Group.objects.create(
            title=ts.GROUP_2_TITLE,
            slug=ts.GROUP_2_SLUG,
            description=ts.GROUP_2_DESCR
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(ts.TEMP_DIR, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.writer = User.objects.create_user(username=ts.WRITER)
        self.reader = User.objects.create_user(username=ts.READER)
        self.writer_client = Client()
        self.writer_client.force_login(self.writer)
        self.reader_client = Client()
        self.reader_client.force_login(self.reader)
        Follow.objects.create(author=self.writer,
                              user=self.reader)
        self.posts = []

        for i in range(3):
            post = Post.objects.create(text=f"Тестовый текст {i}",
                                       author=self.writer,
                                       group=self.group_2,)
            self.posts.append(post)
        for i in range(6):
            post = Post.objects.create(text=f"Тестовый текст {i*10}",
                                       author=self.writer,)
            self.reader.saved_posts.add(post)
            self.posts.append(post)
        for i in range(5):
            post = Post.objects.create(text=f"Тестовый текст {i*100}",
                                       author=self.writer,
                                       group=self.group,)
            self.reader.saved_posts.add(post)
            self.posts.append(post)
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=ts.IMAGE,
            content_type="image/gif")
        post = Post.objects.create(text="Тестовый текст ",
                                   author=self.writer,
                                   group=self.group,
                                   image=uploaded,)
        self.reader.saved_posts.add(post)
        self.posts.append(post)
        self.first_post_id = self.posts[0].id
        self.last_post_id = self.posts[-1].id
        self.SAVE_POST_URL = reverse("save_post",
                                     kwargs={"post_id": self.first_post_id})
        self.REMOVE_POST_URL = reverse("remove_post",
                                       kwargs={"post_id": self.last_post_id})
        self.DELETE_POST_URL = reverse("post_delete",
                                       kwargs={"username": ts.WRITER,
                                               "post_id": self.last_post_id})
        self.EDIT_POST_URL = reverse("post_edit",
                                     kwargs={"username": ts.WRITER,
                                             "post_id": self.first_post_id})
        self.COMMENT_POST_URL = reverse("add_comment",
                                        kwargs={"username": ts.WRITER,
                                                "post_id": self.first_post_id})
        self.POST_URL = reverse("post",
                                kwargs={"username": ts.WRITER,
                                        "post_id": self.last_post_id})

    def tearDown(self):
        cache.clear()

    def test_posts_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            ts.INDEX_URL: "index.html",
            ts.NEW_POST_URL: "new_post.html",
            ts.NEW_GROUP_POST_URL: "new_post.html",
            ts.GROUP_1_URL: "group.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.writer_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_pages_show_correct_context(self):
        """Шаблоны со списком публикаций сформированы с
           правильным контекстом.
           Пост с группой появляется в списке.
        """
        reverse_names = (ts.INDEX_URL,
                         ts.SAVED_POSTS_URL,
                         ts.GROUP_1_URL,
                         ts.PROFILE_URL,
                         )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.reader_client.get(reverse_name)
                first_object = response.context["page"][0]
                post_author_0 = first_object.author
                post_text_0 = first_object.text
                post_pub_date_0 = first_object.pub_date
                post_group_0 = first_object.group
                post_image_0 = first_object.image
                self.assertEqual(post_author_0, self.posts[-1].author)
                self.assertEqual(post_text_0, self.posts[-1].text)
                self.assertEqual(post_pub_date_0, self.posts[-1].pub_date)
                self.assertEqual(post_group_0, self.posts[-1].group)
                self.assertEqual(post_image_0, self.posts[-1].image)

    def test_posts_pages_show_less_than_10_posts(self):
        """В списке публикаций не более 10 постов."""
        reverse_names = (ts.INDEX_URL,
                         ts.SAVED_POSTS_URL,
                         ts.GROUP_1_URL,
                         ts.PROFILE_URL,
                         )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.reader_client.get(reverse_name)
                last_post_index = response.context["page"].end_index()
                self.assertTrue(last_post_index <= PAGE_SIZE)

    def test_post_is_not_in_wrong_group(self):
        """Публикация с группой не появляется на странице другой группы."""
        reverse_name = ts.GROUP_2_URL
        response = self.reader_client.get(reverse_name)
        self.assertNotIn(self.posts[-1],
                         response.context["page"].object_list)

    def test_group_page_shows_correct_context(self):
        """Шаблоны страницы группы сформирован с
            правильным контекстом.
        """
        reverse_name = ts.GROUP_1_URL
        response = self.reader_client.get(reverse_name)
        group = response.context["group"]
        self.assertEqual(group.slug, ts.GROUP_1_SLUG)
        self.assertEqual(group.title, ts.GROUP_1_TITLE)
        self.assertEqual(group.description, ts.GROUP_1_DESCR)

    def test_new_post_page_shows_correct_context(self):
        """Шаблоны страницы создания публикации сформирован с
            правильным контекстом.
        """
        reverse_names = (ts.NEW_GROUP_POST_URL,
                         ts.NEW_POST_URL,
                         self.EDIT_POST_URL)
        form_fields = {"text": forms.fields.CharField, }
        for i, reverse_name in enumerate(reverse_names):
            with self.subTest():
                response = self.writer_client.get(reverse_name)
                if i == 0:
                    group = response.context["group"]
                    self.assertEqual(group.slug, ts.GROUP_1_SLUG)
                    self.assertEqual(group.title, ts.GROUP_1_TITLE)
                    self.assertEqual(group.description, ts.GROUP_1_DESCR)
                else:
                    form_fields["group"] = forms.fields.ChoiceField
                form = response.context["form"]
                for value, expected in form_fields.items():
                    form_field = form.fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблоны страницы профиля сформирован с
            правильным контекстом.
        """
        reverse_name = ts.PROFILE_URL
        response = self.writer_client.get(reverse_name)
        author = response.context["author"]
        posts_count = response.context["posts_count"]
        self.assertEqual(author.username, ts.WRITER)
        self.assertEqual(posts_count, 15)

    def test_post_page_shows_correct_context(self):
        """Шаблоны страницы поста сформирован с
            правильным контекстом.
        """
        reverse_name = self.POST_URL
        response = self.writer_client.get(reverse_name)
        post = response.context["post"]
        self.assertEqual(post.author, self.posts[-1].author)
        self.assertEqual(post.text, self.posts[-1].text)
        self.assertEqual(post.pub_date, self.posts[-1].pub_date)
        self.assertEqual(post.group, self.posts[-1].group)
        self.assertEqual(post.image, self.posts[-1].image)

    def test_post_delete_correct_post(self):
        """Удаление поста работает верно."""
        post_id = self.posts[-1].id
        posts_count = Post.objects.count()
        reverse_name = self.DELETE_POST_URL
        response = self.writer_client.get(reverse_name)
        self.assertEqual(Post.objects.count(), posts_count - 1)
        self.assertTrue(Post.objects.filter(id=post_id).count() == 0)
        self.assertRedirects(response, ts.INDEX_URL)

    def test_post_add_to_saved(self):
        """Пост добавляется в сохранённое правильно."""
        posts_count = self.reader.saved_posts.count()
        reverse_name = self.SAVE_POST_URL
        response = self.reader_client.get(reverse_name)
        self.assertEqual(self.reader.saved_posts.count(),
                         posts_count + 1)
        self.assertRedirects(response, ts.SAVED_POSTS_URL)

    def test_remove_from_saved(self):
        """Пост убирается из сохранённого."""
        posts_count = self.reader.saved_posts.count()
        reverse_name = self.REMOVE_POST_URL
        response = self.reader_client.get(reverse_name)
        self.assertEqual(self.reader.saved_posts.count(),
                         posts_count - 1)
        self.assertRedirects(response, ts.SAVED_POSTS_URL)

    def not_test_index_cached(self):
        """Кэширование главной страницы работает."""
        reverse_name = ts.INDEX_URL
        response = self.writer_client.get(reverse_name)
        content = response.content
        Post.objects.create(text="Новый пост", author=self.writer,)
        response = self.writer_client.get(reverse_name)
        self.assertEqual(content, response.content)
        time.sleep(ts.CACHE_TIMEOUT)
        response = self.writer_client.get(reverse_name)
        self.assertNotEqual(content, response.content)
