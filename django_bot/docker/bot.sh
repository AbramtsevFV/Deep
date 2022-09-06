#!/usr/bin/env bash
set -e

mkdir -p /data/public
cd django_bot
python manage.py run_bot

