# Простая социальная сеть для курса Higload Architect

### Технологии:
- Python 3.10.4
- FastAPI 0.78.0
- MySQL 8.0.29

### Деплой:
1. Склонировать репозиторий в любую директорию
```
cd ~
git clone https://github.com/dmarichuk/otus-simple-social-network
cd otus-simple-social-network
```
2. Создать файл **.env** с переменными окружения
```
# ~/otus-simple-social-network/.env
MYSQL_HOST=db # имя сервиса
MYSQL_DATABASE="otus" # название БД
MYSQL_USER="mysql_user" # пользователь БД
MYSQL_PASSWORD="superpassword" # пароль пользователя
MYSQL_ROOT_PASSWORD="rootpassword" # пароль для рута БД
```
Можно использовать уже имеющийся инстанс БД и вписать туда нужные переменные. Для запуска в контейнере, оставляем _MYSQL_HOST=db_, а остальное меням по собственному представлению
3. Запускаем docker-compose
```
# ~/otus-simple-social-network/
docker-compose up --build -d
```
4. После запуска контейнеров, заходим внутрь контейнера _server_ и инициализируем БД
```
# ~/otus-simple-social-network/
docker-compose exec server sh

/app # python3 init_db.py
[2022-06-27 17:57:57,940][INFO]:: Initialize database...
[2022-06-27 17:57:58,138][INFO]:: Database initialized!
```
5. В браузере открываем _hostname_:8000/redoc.
Тут можно посмотреть эндпоинты и примеры запросов
Так же в репозитории лежит коллекция для Postman - _otusSimpleSocialMedia.postman_collection.json_