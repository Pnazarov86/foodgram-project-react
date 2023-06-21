# Проект - «Продуктовый помощник» (FOODGRAM)

### Описание
Приложение «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Технологии
 - Python 3.9
 - Django 3.2
 - Django REST framework 3.12
 - Docker

# Запуск проекта в dev-режиме на Linux:
 - Клонируйте репозиторий
 - Запоните файл .env секретами, согласно примеру из папки infra
 - В папке infra выполните команду:
``` 
docker-compose up
```
 - Выполнити миграции:
```
sudo docker compose exec backend python manage.py migrate
```
 - Создайте суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```
 - Наполните базу данных ингредиентами:
 ```
 sudo docker compose exec backend python manage.py loaddata ingredients.json
 ```
 - Соберите статику:
```
sudo docker compose exec backend python manage.py collectstatic --noinput
``` 
Проект запустится на адресе http://localhost

### Автор 
Пётр Назаров  
https://github.com/Pnazarov86
