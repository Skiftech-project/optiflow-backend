# skiftech-backend
Репозиторій проекту для розробки backend частини додатку.

Документація API: [https://optiflowbackend.azurewebsites.net/apidocs/](https://optiflowbackend.azurewebsites.net/apidocs/)

Для запуску додатку потрібно завантажити бібліотеки

Перед завантаженням бібліотек потрібно створити віртуальне оточення

Для створення оточення відкрийте командну строку в папці проекту та напишіть
```
python -m venv venv
```
Для активації оточення напишіть у консолі
```
venv\Scripts\activate
```
Після цього в консолі у вас з'явиться надпис (venv)

Для завантаження бібліотек впишіть у консоль
```
pip install -r requirements.txt
```

Створіть файл .env та напишіть у ньому
```.env
SECRET_KEY=<YOUR-SECRET-KEY>
SQLALCHEMY_DATABASE_URI=<YOUR DATABASE URI>
SQLALCHEMY_ECHO=<YOUR-ECHO>
FLASK_JWT_SECRET_KEY=<YOUR-JWT-SECRET-KEY>
```

Додаток використовує docker. Для того, щоб запустити базу даних в фоновому режимі, пропишіть
```
docker-compose up -d
```
Для створення таблиць в базі даних пропишіть
```
flask db upgrade
```

Після цього можна запустити додаток, для цього напишіть 
```
flask run
```