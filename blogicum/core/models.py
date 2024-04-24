from django.db import models


class CreatedAt(models.Model):
    """Абстрактная модель. Добавляет дату создания записи"""

    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Добавлено')

    class Meta:
        abstract = True
        ordering = ('created_at',)


class IsPublishedCreatedAt(CreatedAt):
    """Абстрактная модель. Добавляет флаг is_published.
    и дату создания записи.
    """

    is_published = models.BooleanField(default=True,
                                       verbose_name='Опубликовано',
                                       help_text='Снимите галочку,'
                                       ' чтобы скрыть публикацию.')

    class Meta:
        abstract = True
