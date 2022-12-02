# Чат-бот для викторины
 Бот для Telegram и VK, который проводит викторину - задаёт вопросы и анализирует ответы пользователей.

### Примеры ботов
[Бот в Telegram](https://t.me/dw_dvmn_quiz_bot)

![tg](https://user-images.githubusercontent.com/16899464/203139608-0b2fd5ce-614e-4310-a7e3-e3959ad439e8.gif)

[Бот сообщества в VK](https://vk.com/club217208554)

![vk](https://user-images.githubusercontent.com/16899464/203139624-32eee7f7-b392-4200-84a8-24f4b0a0f520.gif)

### Установка
1. Предварительно должен быть установлен Python3.
2. Для установки зависимостей, используйте команду pip (или pip3, если есть конфликт с Python2) :
```shell
pip install -r requirements.txt
```
3. Для Telegram: необходимо [зарегистрировать бота и получить его API-токен](https://telegram.me/BotFather)
4. [Зарегистрировать](https://redis.com/) базу данных Redis для хранения вопросов пользователю
5. В директории скрипта создайте файл `.env` и укажите в нём следующие данные:

- `QUIZ_FILE` - путь к файлу с вопросами для викторины.
- `TG_BOT_TOKEN` — токен для Telegram-бота, полученный от Bot Father.
- `VK_GROUP_TOKEN` - токен группы ВКонтакте - [см. документацию](https://dev.vk.com/api/access-token/getting-started#%D0%9A%D0%BB%D1%8E%D1%87%20%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0%20%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D1%81%D1%82%D0%B2%D0%B0)
- `ADMIN_USER` — id чата Telegram, куда будут отправляться логи (можно узнать у @userinfobot).
- `REDIS_URL` - url подключения к базе данных Redis, можно получить [в личном кабинете](https://app.redislabs.com) после регистрации 
- `REDIS_PORT` - порт базы данных Redis
- `REDIS_PASSWORD` - пароль для подключения к базе данных Redis

### Запуск ботов 

Запуск Telegram бота :
```shell
$ python tg_bot.py
```

Запуск бота Вконтакте :
```shell
$ python vk_bot.py
```
