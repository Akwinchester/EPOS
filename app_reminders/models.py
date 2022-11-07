from django.db import models
import datetime

class tasks(models.Model):
    task_text = models.CharField(max_length=150, default='', verbose_name='текст задачи')
    deadline = models.DateTimeField(verbose_name='дедлайн', default=datetime.datetime.now())
    task_description = models.TextField(default='')
    priority = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Задачи'
    def __str__(self):
        return f'задача {self.id}'


# class Profile(models.Model):
#     user=models.OneToOneField(User, null=True, on_delete=models.CASCADE)
#     bio=models.TextField(null=True, blank=True)
#     profile_pic = models.ImageField(null=True, blank=True, upload_to="images/profile/")
#     facebook = models.CharField(max_length=50, null=True, blank=True)
#     twitter = models.CharField(max_length=50, null=True, blank=True)
#     instagram = models.CharField(max_length=50, null=True, blank=True)
# def __str__(self):
#     return str(self.user)