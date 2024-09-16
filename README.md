# ![alt text](frontend/src/images/logo-header.png)

**Продуктовый помощник (Foodrgam)** - мой дипломный проект.  
Проект представляет собой онлайн-сервис и API для него.

На этом сервисе пользователи смогут:

- публиковать свои рецепты
- подписываться на публикации других пользователей
- добавлять чужие рецепты в избранное
- подписываться на публикации других авторов
- создавать список продуктов, которые нужно купить для приготовления выбранных блюд


---
Ознакомится с проектом можно здесь:  [Foodrgam](https://foodgram-lipetsk.ddns.net/recipes)  
Спецификация API: [ReDoc](https://foodgram-lipetsk.ddns.net/api/docs/)

[![Main Foodgram workflow](https://github.com/K-u-n-i-n/foodgram/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/K-u-n-i-n/foodgram/actions/workflows/main.yml)


## Технологии:


![Python](https://img.shields.io/badge/Python-3.9.13-blue)
![Django](https://img.shields.io/badge/Django-3.2.16-green)
![DjangoRestFramework](https://img.shields.io/badge/DjangoRestFramework-3.12.4-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.10-green)
![Docker](https://img.shields.io/badge/Docker-24.0.5-blue)

![Docker](https://img.shields.io/badge/lang-ru-red)

## Особенности реализации
- Проект запускается в четырёх контейнерах — gateway, db, backend и frontend;
- Образы foodgram_frontend, foodgram_backend и foodgram_gateway запушены на DockerHub;
- Реализован workflow c автодеплоем на удаленный сервер и отправкой сообщения в Telegram;

## Развертывание на локальном сервере

- Создайте файл .env в корне проекта. Шаблон для заполнения файла находится в .env.example;
- Установите Docker и docker-compose (Про установку вы можете прочитать в [документации](https://docs.docker.com/engine/install/) и [здесь](https://docs.docker.com/compose/install/) про установку docker-compose.)
- Запустите docker compose, выполнив команду: `docker compose -f docker-compose.yml up --build -d`.
- Выполните миграции: `docker compose -f docker-compose.yml exec backend python manage.py migrate`.
- Создайте суперюзера: `docker compose -f docker-compose.yml exec backend python manage.py createsuperuser`.
- Соберите статику: `docker compose -f docker-compose.yml exec backend python manage.py collectstatic`.
- Заполните базу ингредиентами: `docker compose -f docker-compose.yml exec backend python manage.py load_ingredients`.
- Зайдите в админку и создайте теги для рецептов.
  
## Авторы
backend: <span style="color: green;">*Кунин Александр*</span> (K.u.n.i.n@yandex.ru)  
frontend: <span style="color: green;">*Яндекс Практикум*</span> ([Яндекс Практикум](https://yandex.ru/support/practicum/))