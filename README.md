![example workflow](https://github.com/AndreyLeshchev/foodgram-project-react/workflows/Foodgram%20workflow/badge.svg) 
# Foodgram
Foodgram — онлайн-сервис для создания и обмена рецептами блюд.

Ссылка на сайт:  
```
[https://recipesfood.hopto.org/](https://recipesfood.hopto.org/)
```

## Используемые технологии:
* Python
* Django
* Django REST Framework + Djoser
* Nginx
## Как запустить проект:

1. Клонировать репозиторий и перейти в него в командной строке:

    ```
    git clone git@github.com:AndreyLeshchev/foodgram-project-react.git
    ```
    ```
    cd backend
    ```

    Cоздать и активировать виртуальное окружение:
    
    ```
    python3 -m venv env
    ```
    
    * Если у вас Linux/macOS
    
        ```
        source env/bin/activate
        ```
    
    * Если у вас windows
    
        ```
        source venv/Scripts/activate
        ```
    
    Установить зависимости из файла requirements.txt:

    ```
    python -m pip install --upgrade pip
    ```
    ```
    pip install -r requirements.txt
    ```
    
    Выполнить миграции:

    ```
    python manage.py migrate
    ```

    Запустить проект:
    ```
    python manage.py runserver
    ```
    
    Для переменных окружения в директории проекта создаем файл .env.example со следующим содержимым: 
    
    ```
    - POSTGRES_USER — имя пользователя БД (необязательная переменная, значение по умолчанию — postgres);
    - POSTGRES_PASSWORD — пароль пользователя БД (обязательная переменная для создания БД в контейнере);
    - POSTGRES_DB — название базы данных (необязательная переменная, по умолчанию совпадает с POSTGRES_USER).
    - DB_HOST — адрес, по которому Django будет соединяться с базой данных. При работе нескольких контейнеров в сети Docker network вместо адреса указывают имя контейнера, где запущен сервер БД, — в нашем случае это контейнер db.
    - DB_PORT — порт, по которому Django будет обращаться к базе данных. 5432 — это порт по умолчанию для PostgreSQL.
    - DEBUG = включать/выключать отладочный режим приложения в зависимости от текущего окружения (необязательная переменная, значение по умолчанию — False)
    - ALLOWED_HOSTS = список хостов/доменов, для которых может работать текущий сайт (необязательная переменная, значение по умолчанию — 127.0.0.1, localhost).
    - CSRF_TRUSTED_ORIGINS - список хостов/доменов, для доступа в админ зону.
    - USE_DB - возможность сменить базу данных sqlite/postgresql (необязательная переменная, значение по умолчанию — postgresql).
    ```
2. Подготовка проекта для развертывания на сервере:
   
    Создать Docker образы:
    ```
    cd frontend
    docker build -t username/foodgram_frontend .
    cd ../backend
    docker build -t username/foodgram_backend .
    cd ../nginx
    docker build -t username/foodgram_gateway . 
    ```
    Загрузить на DockerHub:
    ```
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    docker push username/foodgram_gateway
    ```
3. Деплой на сервер:

   Подключитесь к удаленному серверу:
   ```
   ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
   ```
   Создайте на сервере директорию foodgram через терминал:
   ```
   mkdir foodgram
   ```
   Установка docker compose на сервер:
   ```
   sudo apt update
   sudo apt install curl
   curl -fSL https://get.docker.com -o get-docker.sh
   sudo sh ./get-docker.sh
   sudo apt-get install docker-compose-plugin
   ```
   В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env.example:
   ```
   scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
   * ath_to_SSH — путь к файлу с SSH-ключом;
   * SSH_name — имя файла с SSH-ключом (без расширения);
   * username — ваше имя пользователя на сервере;
   * server_ip — IP вашего сервера.
   ```
   Запустите docker compose в режиме демона:
   ```
   sudo docker compose -f docker-compose.production.yml up -d
   ```
   Выполните миграции, загрузите данные в базу данных, соберите статические файлы бэкенда и скопируйте их в /backend_static/static/:
   ```
   sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
   sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
   sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_tags
   sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
   sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
   ```
   На сервере в редакторе nano откройте конфиг Nginx и измените настройки location в секции server:
   ```
   sudo nano /etc/nginx/sites-enabled/default
   ```
   ```
   location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
   }
   ```
   Выполните проверку конфигурации, если нет ошибок, то перезапускаем Nginx:
   ```
   sudo nginx -t

   sudo service nginx reload
   ```

## Примеры запросов к API:

* После запуска проекта будет доступна документация по адресу:

   ```
   https://127.0.0.1:8000/api/docs/
   ```

* Для получение специального токена необходимо отправить запрос по адресу:

  > POST http://127.0.0.1:8000/api/auth/token/login/

  Пример запроса:

  ```
  {
  "password": "string",
  "email": "string"
  }
  ```
* Для получения всех рецептов необходимо отправить запрос по адресу:
  
  > GET http://127.0.0.1:8000/api/recipes/

  Пример ответа:
  
  ```
  {
    "count": 123,
    "next": "http://foodgram.example.org/api/recipes/?page=4",
    "previous": "http://foodgram.example.org/api/recipes/?page=2",
    "results": [
      {
        "id": 0,
        "tags": [
          {
            "id": 0,
            "name": "Завтрак",
            "color": "#E26C2D",
            "slug": "breakfast"
          }
        ],
        "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
        },
        "ingredients": [
          {
            "id": 0,
            "name": "Картофель отварной",
            "measurement_unit": "г",
            "amount": 1
          }
        ],
        "is_favorited": true,
        "is_in_shopping_cart": true,
        "name": "string",
        "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
        "text": "string",
        "cooking_time": 1
      }
    ]
  }
  ```

* Для добавления рецепта в избранное необходимо отправить запрос по адресу:

  > POST http://127.0.0.1:8000/api/recipes/{id}/favorite/
  
  Пример ответа:
    
  ```
  {
    "id": 0,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "cooking_time": 1
  }
  ```

### Автор - [Андрей Лещев](https://github.com/AndreyLeshchev)
