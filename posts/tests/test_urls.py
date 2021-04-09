from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

import posts.tests.settings as ts
from posts.models import Follow, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        for i in range(4):
            post = Post.objects.create(text=f'Тестовый текст {i}',
                                       author=self.writer,
                                       group=self.group,
                                       )
            self.posts.append(post)
        self.first_post_id = self.posts[0].id
        self.last_post_id = self.posts[-1].id
        self.SAVE_POST_URL = reverse('save_post',
                                     kwargs={'post_id': self.last_post_id})
        self.REMOVE_POST_URL = reverse('remove_post',
                                       kwargs={'post_id': self.last_post_id})
        self.DELETE_POST_URL = reverse('post_delete',
                                       kwargs={'username': ts.WRITER,
                                               'post_id': self.first_post_id})
        self.EDIT_POST_URL = reverse('post_edit',
                                     kwargs={'username': ts.WRITER,
                                             'post_id': self.first_post_id})
        self.COMMENT_POST_URL = reverse('add_comment',
                                        kwargs={'username': ts.WRITER,
                                                'post_id': self.first_post_id})
        self.POST_URL = reverse('post',
                                kwargs={'username': ts.WRITER,
                                        'post_id': self.first_post_id})

    def tearDown(self):
        cache.clear()

    def test_urls_exist_at_desired_location(self):
        '''Проверка доступности адресов любому пользователю.'''
        urls = (ts.INDEX_URL,
                ts.GROUPS_INDEX_URL,
                ts.GROUP_1_URL,
                ts.SEARCH_URL,
                ts.PROFILE_URL,
                self.POST_URL,
                )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_exist_at_desired_location_authorized(self):
        '''Проверка доступности адресов авторизованному пользователю.'''
        reverse_names = (ts.NEW_GROUP_POST_URL,
                         ts.NEW_POST_URL,
                         ts.NEW_GROUP_URL,
                         ts.GROUP_1_URL,
                         ts.SAVED_POSTS_URL,
                         self.EDIT_POST_URL,
                         )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.writer_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_at_desired_location_authorized_not_author(self):
        '''Проверка перенаправления авторизованного пользователя
            не автора поста
        '''
        reverse_names = (self.EDIT_POST_URL,
                         self.DELETE_POST_URL,
                         )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.reader_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_redirect_at_desired_location_authorized(self):
        '''
            Проверка перенаправления авторизованного пользователю
            после изменения поста.
        '''
        reverse_names = (self.DELETE_POST_URL,
                         self.SAVE_POST_URL,
                         self.REMOVE_POST_URL,
                         self.COMMENT_POST_URL,
                         )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.writer_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_redirect_at_desired_location(self):
        '''Проверка перенаправления анонимного пользователя.'''
        reverse_names = (ts.NEW_POST_URL,
                         ts.NEW_GROUP_POST_URL,
                         ts.NEW_GROUP_URL,
                         self.DELETE_POST_URL,
                         self.EDIT_POST_URL,
                         self.SAVE_POST_URL,
                         self.REMOVE_POST_URL,
                         self.COMMENT_POST_URL,
                         ts.SAVED_POSTS_URL,
                         )
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        templates_url_names = {ts.INDEX_URL: 'index.html',
                               ts.NEW_POST_URL: 'new_post.html',
                               ts.NEW_GROUP_URL: 'new_group.html',
                               self.EDIT_POST_URL: 'new_post.html',
                               ts.GROUP_1_URL: 'group.html',
                               ts.PROFILE_URL: 'profile.html',
                               ts.FOLLOW_INDEX_URL: 'follow_index.html',
                               ts.GROUPS_INDEX_URL: 'groups_index.html',
                               ts.SAVED_POSTS_URL: 'saved.html',
                               }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.writer_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_non_existent_url_return_404(self):
        '''Возвращает код 404, если страница не найдена.'''
        response = self.guest_client.get(ts.NON_EXISTENT_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
