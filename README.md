# Foodgram - Продуктовый помощник
## Описание проекта
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
### Стек технологий и библиотек проекта
- Django 3.2
- Django Rest Framework 3.12.4
- Python 3.9
- Docker
- Gunicorn 20.1
- Nginx
- Yandex Cloud
- Nginx
- GitHub Actions
- PostgreSQL

### Адрес сервера, на котором запущен проект:
```sh
https://myfoodgram.bounceme.net/
```
### Спецификация проекта с возможными запросами доступна по адресу:
```sh
https://myfoodgram.bounceme.net/api/docs/
```
### Реквизиты для входа в зону администрации:
| Имя пользователя | Email | Пароль |
| ------ | ------ | ------ |
| admin | admin@mail.ru | g4h01m_minad |

### Запуск проекта локально:
Склонируйте репозиторий на свой компьютер:
```sh
git@github.com:Diavolution/foodgram-project-react.git
```
В корневой директории создайте файл .env и заполните его собственными данными:
```sh
SECRET_KEY=my_secret_key
DEBUG=True
DB_NAME=my_db_name
DB_USER=my_db_user
DB_PASSWORD=my_db_password
DB_HOST=my_db_host
```
Перейдите в директорию infra и выполните создание и запуск контейнеров Docker:
```sh
cd infra
docker compose -f docker-compose.yml up -d
```
Выполните команду сборки статики:
```sh
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
После этого выполните команду копирования собранных файлов:
```sh
docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```
Примените миграции:
```sh
docker compose -f docker-compose.yml exec backend python manage.py migrate
```
Создайте суперпользователя и загрузите в базу ингредиенты:
```sh
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
docker compose -f docker-compose.yml exec backend python manage.py load_csv_data
```
В админ-зоне добавьте теги.
