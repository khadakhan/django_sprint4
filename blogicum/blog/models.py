from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import CreatedAt, IsPublishedCreatedAt
from .const import CHAR_LENGTH, NAME_LENGTH_LIMIT

User = get_user_model()


class Category(IsPublishedCreatedAt):
    title = models.CharField(
        max_length=CHAR_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы '
        'латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:NAME_LENGTH_LIMIT]


class Location(IsPublishedCreatedAt):
    name = models.CharField(
        max_length=CHAR_LENGTH,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:NAME_LENGTH_LIMIT]


class Post(IsPublishedCreatedAt):
    title = models.CharField(
        max_length=CHAR_LENGTH,
        verbose_name='Название'
    )
    text = models.TextField(
        'Текст'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        default=timezone.now(),  # чтобы автоматом устанавливалось текущее время
        help_text='Если установить дату и время в '
        'будущем — можно делать отложенные '
        'публикации.'
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Местоположение',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Категория',
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def get_absolute_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.author.username})

    def __str__(self):
        return self.title[:NAME_LENGTH_LIMIT]


class Comment(CreatedAt):
    text = models.TextField(
        'Текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )

    class Meta(CreatedAt.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:NAME_LENGTH_LIMIT]
