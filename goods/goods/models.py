from django.db import models


class Tags(models.Model):
    name = models.CharField("Название тега", max_length=60)


class Ad(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.UUIDField(default=0)
    title = models.CharField("Название объявления", max_length=60)
    description = models.TextField("Описание объявления")
    price = models.PositiveIntegerField("Цена")
    date = models.DateTimeField("Дата и время", auto_now_add=True)
    tag = models.ForeignKey(
        Tags, related_name="tags", on_delete=models.CASCADE, default=0
    )
    views = models.PositiveIntegerField(default=0, auto_created=True)
    img_src = models.FileField(upload_to="items", null=True)
