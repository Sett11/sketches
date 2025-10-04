#!/bin/bash
# Скрипт для запуска парсера через cron
# Использование: добавьте в crontab:
# 0 8 * * * /root/download_files/run_parser.sh

# Переход в директорию проекта
cd /root/download_files || exit 1

# Запуск парсера через docker compose (v2)
/usr/bin/docker compose run --rm parser >> /root/download_files/data/logs/cron_$(date +\%Y\%m\%d_\%H\%M\%S).log 2>&1

# Код возврата
exit $?

