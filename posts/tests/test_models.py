import textwrap

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

import posts.tests.settings as ts
from posts.models import Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=ts.GROUP_1_TITLE,
            slug=ts.GROUP_1_SLUG,
            description=ts.GROUP_1_DESCR
        )

    def test_verbose_name(self):
        '''verbose_name в полях совпадает с ожидаемым.'''
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Заголовок',
            'description': 'Описание',
            'slug': 'Идентификатор',
        }
        for value, expected in field_verboses.items():
            verbose_name = group._meta.get_field(value).verbose_name
            with self.subTest(value=value):
                self.assertEqual(verbose_name, expected)

    def test_help_text(self):
        '''help_text в полях совпадает с ожидаемым.'''
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Дайте короткое название сообществу.',
            'description': 'Опишите сообщество подробно.',
            'slug': 'Укажите идентификатор для сообщества.',
        }
        for value, expected in field_help_texts.items():
            help_text = group._meta.get_field(value).help_text
            with self.subTest(value=value):
                self.assertEqual(help_text, expected)

    def test_object_name_is_title_fild(self):
        '''В поле __str__  объекта task записано значение поля group.title.'''
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username=ts.WRITER)
        authorized_client = Client()
        authorized_client.force_login(user)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=user
        )

    def test_verbose_name(self):
        '''verbose_name в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'image': 'Изображение',
            'group': 'Группа',
            'saved': 'Сохранённое',
        }
        for value, expected in field_verboses.items():
            verbose_name = post._meta.get_field(value).verbose_name
            with self.subTest(value=value):
                self.assertEqual(verbose_name, expected)

    def test_help_text(self):
        '''help_text в полях совпадает с ожидаемым.'''
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Напишите сообщение.',
            'image': 'Загрузите картинку.',
            'group': 'Здесь можно выбрать сообщество.',
        }
        for value, expected in field_help_texts.items():
            help_text = post._meta.get_field(value).help_text
            with self.subTest(value=value):
                self.assertEqual(help_text, expected)

    def test_object_name_is_text_field(self):
        '''В поле __str__  объекта post записано верное значение.'''
        post = PostModelTest.post
        if post.group is None:
            expected_object_name = (f'{post.author.first_name} '
                                    f'{post.author.last_name}, '
                                    f'публикация от {post.pub_date:%d.%m.%Y}: '
                                    f'{textwrap.wrap(post.text, 15)[0]}')
        else:
            expected_object_name = (f'{post.author.first_name} '
                                    f'{post.author.last_name}, '
                                    f'публикация от {post.pub_date:%d.%m.%Y} '
                                    f'в сообществе {post.group.title} '
                                    f'{textwrap.wrap(post.text, 15)[0]}')
        self.assertEqual(expected_object_name, str(post))
