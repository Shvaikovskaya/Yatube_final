import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.settings as ts
from posts.models import Group, Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.uploaded_image = SimpleUploadedFile(name='image.gif',
                                                content=ts.IMAGE,
                                                content_type='image/gif'
                                                )
        cls.group = Group.objects.create(
            title=ts.GROUP_1_TITLE,
            slug=ts.GROUP_1_SLUG,
            description=ts.GROUP_1_DESCR
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.writer = User.objects.create_user(username=ts.WRITER)
        self.writer_client = Client()
        self.writer_client.force_login(self.writer)
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.writer,
                                        group=self.group,)
        self.EDIT_POST_URL = reverse('post_edit',
                                     kwargs={'username': ts.WRITER,
                                             'post_id': self.post.id})

    def test_create_post(self):
        '''При отправки формы создается запись и
           происходит редирект на главную.
        '''
        group = Group.objects.get(slug=ts.GROUP_1_SLUG)
        posts_count = Post.objects.count()
        form_data = {
            'group': group.pk,
            'text': 'Тестовый текст',
            'image': PostCreateFormTests.uploaded_image,
        }
        response = self.writer_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, ts.INDEX_URL)

    def test_create_group(self):
        '''При отправки формы создается сообщество и
           происходит редирект на список сообществ.
        '''
        groups_count = Group.objects.count()
        form_data = {
            'slug': ts.GROUP_3_SLUG,
            'title': ts.GROUP_3_TITLE,
            'description': ts.GROUP_3_DESCR,
        }
        response = self.writer_client.post(
            reverse('new_group'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Group.objects.count(), groups_count + 1)
        self.assertTrue(Group.objects.filter(slug=ts.GROUP_3_SLUG))
        self.assertRedirects(response, ts.GROUPS_INDEX_URL)

    def test_create_post_in_group(self):
        '''При отправки формы создается запись в сообществе и
           происходит редирект на страницу сообщества.
        '''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.writer_client.post(
            ts.NEW_GROUP_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, ts.GROUP_1_URL)

        def test_edit_post(self):
            '''При редактировании через форму меняется запись'''
            posts_count = Post.objects.count()
            response = self.writer_client.get(self.EDIT_POST_URL)
            form = response.context['form']
            data = form.initial
            data['text'] = 'Новый текст'
            response = self.writer_client.post(self.EDIT_POST_URL, data)
            self.assertEqual(Post.objects.count(), posts_count)
            response = self.writer_client.get(self.EDIT_POST_URL)
            self.assertContains(response, 'Новый текст')
            self.assertEqual(response.context['form'].initial['text'],
                             'Новый текст')
