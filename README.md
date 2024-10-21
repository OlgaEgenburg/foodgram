1. Описание проекта
Проект Foodgram - сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.


2. Как запустить проект локально:
Клонировать репозиторий и перейти в него в командной строке

Cоздать и активировать виртуальное окружение:
Windows

python -m venv venv source venv/Scripts/activate

Linux/macOS

python3 -m venv venv source venv/bin/activate

Обновить PIP
Windows

python -m pip install --upgrade pip

Linux/macOS

python3 -m pip install --upgrade pip

Установить зависимости из файла requirements.txt:
pip install -r requirements.txt

Выполнить миграции:
Windows

python manage.py makemigrations python manage.py migrate

Linux/macOS

python3 manage.py makemigrations python3 manage.py migrate

Запустить проект:
Windows

python manage.py runserver

Linux/macOS

python3 manage.py runserver

Загрузить файлы cdv в базу данных:
python manage.py get_ingredient


3. В файле .env должны находиться переменные:
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DB_HOST
DB_PORT
SECRET_KEY
DEBUG

4. Примеры эндпоинтов:
GET http://localhost/api/ingredients/
Response example:
[
    {
        "id": 0,
        "name": "Капуста",
        "measurement_unit": "кг"
    }
]
POST http://localhost/api/users/

{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": "Qwerty123"
}
Response example:
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Иванов"
}
5. Автор проекта:
Эгенбург Ольга (адрес где развернут добавлю позже, когда сделаю деплой)