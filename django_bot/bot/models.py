from django.db import models


class UserTg(models.Model):
    user_id = models.CharField(max_length=255, unique=True, verbose_name="ID пользователя телеграмм")
    user_name = models.CharField(max_length=2500, blank=True, verbose_name="Имя пользователя")

    class Meta:
        verbose_name = "Пользователь телеграмма"
        verbose_name_plural = "Пользователи телеграмма"

    def __str__(self):
        return str(self.user_name)


class RequestResponse(models.Model):
    user = models.ForeignKey(UserTg, verbose_name='Пользователь', on_delete=models.CASCADE)
    request = models.TextField(verbose_name="Вопрос пользователя")
    response = models.TextField(verbose_name="Ответ системы")

    class Meta:
        verbose_name = "Запрос ответ"
        verbose_name_plural = "Запросы ответы"

    def __str__(self):
        return str(self.user)


class StandardMessages(models.Model):
    command = models.CharField(max_length=255, verbose_name='Команда бота')
    message = models.TextField(verbose_name="Текст для пользователя")

    class Meta:
        verbose_name = "Стандартное сообщение"
        verbose_name_plural = "Стандартные сообщения"

    def __str__(self):
        return str(self.command)
