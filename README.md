# Команды #
**Сборка приложения**
```
docker-compose up --build -d
```
**Миграции**
```
docker exec -it app python manage.py migrate
```
**Тесты**
```
docker exec -it app python manage.py test -v 2
```
