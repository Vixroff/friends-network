# **Сервис друзей**

## **Технологии**

- **Django REST Framework**
- **Docker**
- **PostgreSQL**

---

## **Запуск**

Запуск приложения осуществляется в собранных контейнерах Docker. Для этого необходимо иметь установленный и запущенный docker engine. И выполнить следующие шаги.

**1. Клонирование проекта**

```
git clone https://github.com/Vixroff/friends-network.git
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

## **Примеры пользованием API**

Сервис предлагает пользователям следующие функциональные возможности:

- [Регистрация пользователей](#регистрация-пользователей)
- [Аутентификация](#аутентификация)
- [Запрос на дружбу](#запрос-на-дружбу)
- [Просмотр входящих и исходящих запросов на дружбу](#просмотр-входящих-и-исходящих-запросов-на-дружбу)
- [Принять/отклонить запрос на дружбу](#принятьотклонить-запрос-на-дружбу)
- [Просмотр списка друзей](#просмотр-списка-друзей)
- [Удаление из друзей](#удаление-из-друзей)
- [Получить статус отношений с пользователем](#получить-статус-взаимотношений-с-пользователем)

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

HTTP 201 — Пользователь зарегистрирован.

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

HTTP 200 — Токены аутентификации.

```
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY4Mzk3Mjc3MCwiaWF0IjoxNjgzNTQwNzcwLCJqdGkiOiIwMzJkNjJkZDI0ZjQ0NGZmOTI3MzhjYWQyNjk3MzAzZSIsInVzZXJfaWQiOiJkN2JkMGUxOC03ZjcwLTRhZDYtYjIzMC1iM2UwMjA1NjcwYzIifQ.Ss9ulujBevY4oJ_jfgxjn1Ckt9gf1zeo20JeL6-JDcQ",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI3MTcwLCJpYXQiOjE2ODM1NDA3NzAsImp0aSI6IjZkMDdjNzI1ZDk2OTQzYWE4OWUxMzhkMGVhOGJkNTQ1IiwidXNlcl9pZCI6ImQ3YmQwZTE4LTdmNzAtNGFkNi1iMjMwLWIzZTAyMDU2NzBjMiJ9.EkJHxcmCBGFBYLyLGBfxBDuqJg6h4SoWRSFvZAVHL30"
}
```

### **Запрос на дружбу**

**Запрос**

```
curl -X POST "localhost:8000/api/v1/requests/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI3MTcwLCJpYXQiOjE2ODM1NDA3NzAsImp0aSI6IjZkMDdjNzI1ZDk2OTQzYWE4OWUxMzhkMGVhOGJkNTQ1IiwidXNlcl9pZCI6ImQ3YmQwZTE4LTdmNzAtNGFkNi1iMjMwLWIzZTAyMDU2NzBjMiJ9.EkJHxcmCBGFBYLyLGBfxBDuqJg6h4SoWRSFvZAVHL30" \
-d "{
    \"request_friendship_to_user\": \"9225404c-ba85-4035-9d1a-a56b08bd92a2\"
    
}"
```

**Ответ**

HTTP 201 — Запрос на дружбу сформирован.

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

**Ответ в случае встречного запроса на дружбу**

- HTTP 201 — Дружба подтверждена.

```
{
    "id": "0e26a5c8-81fa-4d6b-840f-e87ea60e9ab5",
    "friend_sender": {
        "id": "9225404c-ba85-4035-9d1a-a56b08bd92a2",
        "username": "user2"
    },
    "friend_recipient": {
        "id": "d7bd0e18-7f70-4ad6-b230-b3e0205670c2",
        "username": "user1"
    },
    "status": "Friends",
    "created_at": "2023-05-08T10:14:29.404134Z",
    "updated_at": "2023-05-08T10:20:29.404171Z"
}
```

Здесь можно заметить, что произошло автоматическое подтверждение дружбы **{"status": "Friends"}** на первоначально отправленную заявку пользователем user2.

### **Просмотр входящих и исходящих запросов на дружбу**

**Запрос**

```
curl -X GET "localhost:8000/api/v1/requests/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE" \
```
Запрос может включать в URL следующие параметры:
- ?incoming - покажет все входящие запросы. (localhost:8000/api/v1/requests?incoming);
- ?outgoing - покажет все исходящие запросы. (localhost:8000/api/v1/requests?outgoing);

**Ответ**

HTTP 200 — Список запросов на дружбу.

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
curl -X PUT "localhost:8000/api/v1/requests/bfc9651a-83e8-4dfb-9f0e-a620e1278093/" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE" \
-d "{
    \"accept\": true
}"
```

Тело запроса должно содержать boolean type:
- true - принять дружбу;
- false - отклонить дружбу;

**Ответ**

HTTP 200 — Запрос принят/отклонен.

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
curl -X GET "localhost:8000/api/v1/friendships/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE"
```

**Ответ**

HTTP 200 — Список друзей

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

HTTP 204 — Пользователь удален из друей

### **Получить статус взаимотношений с пользователем**

**Запрос**

```
curl -X GET "localhost:8000/api/v1/relations/user3" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgzNjI4MzAyLCJpYXQiOjE2ODM1NDE5MDIsImp0aSI6ImMyODk4NWYwNGMxOTQ4M2VhNmYwNTViNGJkZjk3ZTIyIiwidXNlcl9pZCI6IjkyMjU0MDRjLWJhODUtNDAzNS05ZDFhLWE1NmIwOGJkOTJhMiJ9.1HeXXzawEnSimfoMRU-eaW14itLePh8QKMwTvTt1qSE"
```

**Ответ**

HTTP 200 — Дружба, заявка в ожидании, запрорс отклонен. 

HTTP 204 — Отношений не найдено.

HTTP 404 — Пользователя не существует.

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
    "status": "Rejected",
    "created_at": "2023-05-08T10:33:07.975116Z",
    "updated_at": "2023-05-08T10:33:07.975135Z"
}
```

---

## **Тестирование**

Были протестированы основные основные функциональные возможности приложения и их пограничные состояния.

**Регистрация**
- Любой пользователь может зарегистрироваться;
- Регистрация с существующим username недоступна;

**Запросы на дружбу**
- Зарегистрированный пользователь успешно может отправить запрос на дружбу;
- Встречный запрос на дружбу автоматически подтверждает дружбу;
- Отправка запроса самому себе недоступна;
- Повторная отправка запроса тому же пользователю недоступна;
- Незарегистрированный пользователь не сможет отправить запрос;
- Дополнительные чувствительные данные не влияют на поведение модели;

**Просмотр запросов на дружбу**
- Зарегистрированный пользователь сможет просмотреть все входящие/исходящие запросы;
- Зарегистрированный пользователь с помощью добавленных параметров к URL запроса сможет разделить входящие/исходящие заявки;
- Незарегистрированный пользователь не сможет просмотреть заявки;

**Принять/отклонить запрос на дружбу**
- Пользователь получатель сможет принять/отклонить входящий запрос;
- Отправитель не может повлиять на отправленный запрос;
- Незарегистрированный пользователь не сможет просмотреть и повлиять на заявку;

**Просмотр списка друзей**
- Зарегистрированный пользователь сможет посмотреть список всех друзей;
- Необработанные, или отвергнутые запросы не попадут в список подтвержденных дружеских;
- Зарегистрированный пользователь сможет просмотреть детально каждую подтвержденную дружескую заявку;
- Зарегистрированный пользователь сможет удалить из друзей пользователя;

**Получить статус дружбы с пользователем**
- Зарегистрированный пользователь сможет узнать статус дружбы с другим существующим пользователем.
- Зарегистрированный пользователь получит 204 в случае отсутвия отношений;
- Запрос на несуществующего пользователя вернет 404;

#### **Запуск тестов**
```
docker exec -it app python manage.py test
```

---
