from django.db import models


class Ad(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('Название объявления', max_length=60)
    description = models.TextField('Описание объявления')
    price = models.PositiveIntegerField('Цена')
    date = models.DateTimeField('Дата и время', auto_now_add=True)
    TAGS = (
        (1, 'Транспорт'),
        (2, 'Личные вещи'),
        (3, 'Для дома и дачи'),
        (4, 'Бытовая электроника'),
        (5, 'Хобби и отдых'),
        (6, 'Недвижимость'),
        (7, 'Работа'),
        (8, 'Услуги'),
        (9, 'Для бизнеса'),
        (10, 'Животные'),
    )
    tag = models.IntegerField('Тип объявления', choices=TAGS)
    views = models.PositiveIntegerField(default=0, editable=False)
    img_src = models.FileField(upload_to='items')

