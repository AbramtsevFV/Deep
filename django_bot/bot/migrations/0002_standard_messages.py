# Generated by Django 4.1.1 on 2022-09-06 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Standard_messages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "command",
                    models.CharField(max_length=255, verbose_name="Команда бота"),
                ),
                ("message", models.TextField(verbose_name="Текст для пользователя")),
            ],
            options={
                "verbose_name": "Стандартное сообщение",
                "verbose_name_plural": "Стандартные сообщения",
            },
        ),
    ]
