import textwrap

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Класс сообщества."""
    title = models.CharField("Заголовок",
                             max_length=200,
                             help_text="Дайте короткое название сообществу.")
    slug = models.SlugField("Идентификатор",
                            unique=True,
                            help_text="Укажите идентификатор для сообщества.")
    description = models.TextField("Описание",
                                   help_text="Опишите сообщество подробно.")

    class Meta:
        """Мета-класс сообщества."""
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

        ordering = ("title",)

    def __str__(self):
        return str(self.title)


class Post(models.Model):
    """Класс публикации."""
    text = models.TextField("Текст",
                            help_text="Напишите сообщение.")
    pub_date = models.DateTimeField("Дата публикации",
                                    auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(User,
                               verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="posts")
    image = models.ImageField(verbose_name="Изображение",
                              upload_to="posts/",
                              blank=True,
                              null=True,
                              help_text="Загрузите картинку.")
    group = models.ForeignKey(Group,
                              verbose_name="Группа",
                              on_delete=models.SET_NULL,
                              related_name="posts",
                              blank=True,
                              null=True,
                              help_text="Здесь можно выбрать сообщество.")
    saved = models.ManyToManyField(User,
                                   verbose_name="Сохранённое",
                                   related_name="saved_posts",
                                   blank=True,)

    class Meta:
        """Мета-класс публикации."""
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-pub_date", "author",)

    def __str__(self):
        if self.group is None:
            return (f"{self.author.first_name} {self.author.last_name}, "
                    f"публикация от {self.pub_date:%d.%m.%Y}: "
                    f"{textwrap.wrap(self.text, 15)[0]}")
        else:
            return (f"{self.author.first_name} {self.author.last_name}, "
                    f"публикация от {self.pub_date:%d.%m.%Y} "
                    f"в сообществе {self.group.title} "
                    f"{textwrap.wrap(self.text, 15)[0]}")


class Comment(models.Model):
    """Класс комментария."""
    post = models.ForeignKey(Post,
                             verbose_name="Публикация",
                             on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User,
                               verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField("Текст",
                            help_text="Напишите комментарий.")
    created = models.DateTimeField("Дата",
                                   auto_now_add=True)

    class Meta:
        """Мета-класс публикации."""
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("post", "-created", "author",)

    def __str__(self):
        return (f"{self.author.first_name} {self.author.last_name}, "
                f"{self.created:%d.%m.%Y} "
                f"написал: {textwrap.wrap(self.text, 15)[0]}")


class Follow(models.Model):
    """Класс подписки."""
    user = models.ForeignKey(User,
                             verbose_name="Подписчик",
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User,
                               verbose_name="Автор",
                               on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        """Мета-класс подписки."""
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
