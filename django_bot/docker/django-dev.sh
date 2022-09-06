#!/usr/bin/env bash
set -e

mkdir -p /data/public
cd django_bot
python manage.py migrate
python manage.py runserver --settings=django_bot.settings 0.0.0.0:8000 && python manage.py run_bot

