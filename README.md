# MyShows Analysis

https://myshows.me/

## Как запустить?
<b>База (только графики)</b>:
* docker pull grih9/myshows_analysis:latest
* docker run -p 5000:5000 grih9/myshows_analysis:latest

<b>Расширенный (включая скрапинг)</b>:
* Клонировать репозиторий (достаточно файлов docker-compose и browsers.json)
* docker pull selenoid/vnc_chrome:100.0
* docker-compose up -d

<b>Добавить датасет</b>:
* docker cp *dataset.csv* *container id*:/app/datasets/custom 

<b>Скопировать датасеты</b>:
* docker cp *container id*:/app/datasets .


Доступ через браузер - http://127.0.0.1:5000/

Selenoid UI - http://127.0.0.1:8080/

Docker Hub - https://hub.docker.com/repository/docker/grih9/myshows_analysis


<b>Полный доступ</b>:
* Запросить конфигурационный файл для доступа к БД (telegram <b>@grih9</b>, vk <b>@grih9</b>)
* Клонировать репозиторий
* Доступ ко всем скриптам через main.py

## Структура проекта
* папки
  * <b>analyze_dataset</b> - содержит методы для анализа csv файлов с последующей записью в БД (млдуль приема данных)
  * <b>API</b> - содержит методы API Flask приложения
  * <b>datasets</b> - содержит все датасеты, папка custom для пользовательских датасетов
  * <b>driver</b> - chrome driver для локального скрапинга (версия chrome 108)
  * <b>filter</b> - модуль фильтрации
  * <b>scrapper</b> - содержит методы для скрапинга эпизодов и шоу (модуль извлечения данных)
  * <b>static</b> - вспомогательные файлы веб-приложения
  * <b>templates</b>  - html-страницы веб-приложения
  * <b>wrappers</b>  - содержит коннектор к базе данных MongoConnector
 * <b>app.py</b>  - файл работы Flask веб-приложения (модуль визализации данных)
 * <b>browsers.json</b> - вспомогательный файл для развертывания контейнеров с браузеров внутри Selenoid
 * <b>constants.py</b> - некоторые используемые константы
 * <b>docker-compose.yml</b> - файл развертывания docker-compose для Selenoid и веб-приложения
 * <b>Dockerfile</b> - фалй контейнеризация веб-приложения
 * <b>main.py</b> - файл содержащий вызовы различных модулей (скрипты)
 * <b>requirements.txt</b> - необходимые зависимости

