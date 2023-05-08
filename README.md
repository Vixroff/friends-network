# Сервис друзей 

## Запуск

Запуск приложения осуществляется в собранных контейнерах Docker. Для этого необходимо иметь установленный и запущенный docker engine. И выполнить следующие шаги.

**1. Клонирование проекта**

```
git clone https://github.com/Vixroff/lol.git
```

**2. Сборка docker контейнеров**

```
docker compose up --build -d
```
**3. Миграции моделей базы данных**

```
docker exec -it app python manage.py migrate
```

---

## Примеры пользования API

Сервис предлагает пользователям следующие функциональные возможности.

### **Регистрация пользователей**

**Запрос**

```
curl -X POST "localhost:8000/api/v1/auth/registration/" \
-H "Content-Type: application/json" \
-d "{
    \"username\": \"user1\",
    \"password\": 12345
}"
```

**Ответ**

HTTP 201

```
{
    "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
    "username": "user1"
}
```

### **Аутентификация**

**Запрос**

```
curl -X POST "localhost:8000/api/v1/auth/token/" \
-H "Content-Type: application/json" \
-d "{
    \"username\": \"user1\",
    \"password\": 12345
}"
```

**Ответ**

HTTP 200

```
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4Mzk3Mjc3MCwiaWF0IjoxNjgzNTQwNzcwLCJqdGkiOiIwMzJkNjJkZDI0ZjQ0NGZmOTI3MzhjYWQyNjk3MzAzZSIsInVzZXJfaWQiOiJkN2JkMGUxOC03ZjcwLTRhZDYtYjIzMC1iM2UwMjA1NjcwYzIifQ.Ss9ulujBevY4oJ_jfgxjn1Ckt9gf1zeo20JeL6-JDcQ",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI3MTcwLCJpYXQiOjE2ODM1NDA3NzAsImp0aSI6IjZkMDdjNzI1ZDk2OTQzYWE4OWUxMzhkMGVhOGJkNTQ1IiwidXNlcl9pZCI6ImQ3YmQwZTE4LTdmNzAtNGFkNi1iMjMwLWIzZTAyMDU2NzBjMiJ9.EkJHxcmCBGFBYLyLGBfxBDuqJg6h4SoWRSFvZAVHL30"
}
```

### **Запрос на дружбу**

**Запрос**

```
curl -L -X POST "localhost:8000/api/v1/requests/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI3MTcwLCJpYXQiOjE2ODM1NDA3NzAsImp0aSI6IjZkMDdjNzI1ZDk2OTQzYWE4OWUxMzhkMGVhOGJkNTQ1IiwidXNlcl9pZCI6ImQ3YmQwZTE4LTdmNzAtNGFkNi1iMjMwLWIzZTAyMDU2NzBjMiJ9.EkJHxcmCBGFBYLyLGBfxBDuqJg6h4SoWRSFvZAVHL30" \
-d "{
    \"request_friendship_to_user\": \"9225404c-ba85-4035-9d1a-a56b08bd92a2\"
    
}"
```

**Ответ**

HTTP 201

```
{
    "id": "0e26a5c8-81fa-4d6b-840f-e87ea60e9ab5",
    "friend_sender": {
        "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
        "username": "user1"
    },
    "friend_recipient": {
        "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
        "username": "user2"
    },
    "status": "Waiting response",
    "created_at": "2023-05-08T10:14:29.404134Z",
    "updated_at": "2023-05-08T10:14:29.404171Z"
}
```

**Ответ в случае обоюдного запроса**

HTTP 201

```
{
    "id": "bfc9651a-83e8-4dfb-9f0e-a620e1278093",
    "friend_sender": {
        "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
        "username": "user1"
    },
    "friend_recipient": {
        "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
        "username": "user2"
    },
    "status": "Friends",
    "created_at": "2023-05-08T10:23:09.608546Z",
    "updated_at": "2023-05-08T10:23:09.608578Z"
}
```

### **Узнать все входящие и исходящие запросы на дружбу**

**Запрос**

```
curl -X GET "localhost:8000/api/v1/requests" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE" \
```
Запрос может включать в URL параметры:
- incoming - покажет все входящие запросы. (localhost:8000/api/v1/requests?incoming)
- outgoing - покажет все исходящие запросы. (localhost:8000/api/v1/requests?outgoing)

**Ответ**

HTTP 200

```
[
    {
        "id": "bfc9651a-83e8-4dfb-9f0e-a620e1278093",
        "friend_sender": {
            "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
            "username": "user1"
        },
        "friend_recipient": {
            "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
            "username": "user2"
        },
        "status": "Waiting response",
        "created_at": "2023-05-08T10:23:09.608546Z",
        "updated_at": "2023-05-08T10:23:09.608578Z"
    },
    {
        "id": "721cd92b-1bfb-474f-88a4-262922b9eceb",
        "friend_sender": {
            "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
            "username": "user2"
        },
        "friend_recipient": {
            "id": "902de654-c87c-4114-8e3b-55259e3674bc",
            "username": "user3"
        },
        "status": "Waiting response",
        "created_at": "2023-05-08T10:33:07.975116Z",
        "updated_at": "2023-05-08T10:33:07.975135Z"
    }
]
```

### **Принять/отклонить запрос на дружбу**

**Запрос**

```
curl -L -X PUT "localhost:8000/api/v1/requests/bfc9651a-83e8-4dfb-9f0e-a620e1278093/accept/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE" \
-d "{
    \"accept\": true
}"
```

Тело запроса включает исключительно boolean type:
- Принять запрос - true
- Отклонить - false

**Ответ**

HTTP 200

```
{
    "id": "bfc9651a-83e8-4dfb-9f0e-a620e1278093",
    "friend_sender": {
        "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
        "username": "user1"
    },
    "friend_recipient": {
        "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
        "username": "user2"
    },
    "friendship": "Accepted",
    "updated_at": "2023-05-08T10:46:02.066944Z"
}
```

### **Просмотр списка друзей**

**Запрос**

```
curl -X GET "localhost:8000/api/v1/friendships" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE"
```

**Ответ**

HTTP 200

```
[
    {
        "id": "bfc9651a-83e8-4dfb-9f0e-a620e1278093",
        "friend_sender": {
            "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
            "username": "user1"
        },
        "friend_recipient": {
            "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
            "username": "user2"
        },
        "status": "Friends",
        "created_at": "2023-05-08T10:23:09.608546Z",
        "updated_at": "2023-05-08T10:46:02.066944Z"
    }
]
```

### **Удаление из друзей**

**Запрос**

```
curl -X DELETE "localhost:8000/api/v1/friendships/bfc9651a-83e8-4dfb-9f0e-a620e1278093/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE"
```

**Ответ**

HTTP 204

### **Получить статус дружбы с пользователем**

**Запрос**

```
curl -X GET "localhost:8000/api/v1/relations/user3" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE"
```

**Ответ**

HTTP 200 if some relation exists, else HTTP 204

```
{
    "id": "721cd92b-1bfb-474f-88a4-262922b9eceb",
    "friend_sender": {
        "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
        "username": "user2"
    },
    "friend_recipient": {
        "id": "902de654-c87c-4114-8e3b-55259e3674bc",
        "username": "user3"
    },
    "status": "Waiting response",
    "created_at": "2023-05-08T10:33:07.975116Z",
    "updated_at": "2023-05-08T10:33:07.975135Z"
}
```





---

**Тесты**
```
docker exec -it app python manage.py test -v 2
```


