from django.db import models
import datetime
class tasks(models.Model):
    task_text = models.CharField(max_length=150, default='', verbose_name='текст задачи')
    deadline = models.DateTimeField(verbose_name='дедлайн', default=datetime.datetime.now())
    task_description = models.TextField(default='')
