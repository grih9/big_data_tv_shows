# big_data_tv_shows
База (только графики):
* docker pull grih9/myshows_analysis:latest
* docker run -p 5000:5000 flask-app

Расширенный (включая скраппинг):
* Клонировать репозиторий (достаточно файлов docker-compose и browsers.json)
* docker pull selenoid/vnc_chrome:100.0
* docker-compose up -d

Доступ через браузер - http://127.0.0.1:5000/
Selenoid UI - http://127.0.0.1:8080/


Полный доступ:
* Запросить конфигурационный файл для доступа к БД (telegram @grih9, vk @grih9)
* Клонировать репозиторий
* Доступ ко всем скриптам через main.py
