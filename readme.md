# Store Telegram Bot + Django Admin

## Описание проекта
Проект позволяет реализовать онлайн-магазин в телеграм-боте. Добавление, редактирование записей и рассылки осуществляются с помощью админ-панели Django.
При разработке использовались библитеки Django и Telebot.

<img width="2117" alt="Тестовое задание" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/d2523821-daea-4a78-ba08-0fe6a2342dff">

## Установка и использование
1. Склонируйте репозиторий.
2. Установите необходимые зависимости, выполнив команду 
```
pip install -r requirements.txt.
```
3. В файле settings.py укажите токены телеграм-бота и провайдера оплаты.
4. Выполните команду
```
python manage.py migrate
```
5. Выполните команду и следуйте инструкциям, чтобы создать учетную запись суперпользователя. Суперпользователь будет иметь доступ к административной панели проекта.
```
python manage.py createsuperuser
```
6. Запустите сервер с помощью команды python manage.py runserver.
7. Запустите бота с помощью команды python manage.py runbot.
8. Для использование административной панели необходимо
    - открыть в веб-бразуере адрес сервера;
    - ввести учетные данные суперпользователя
  
Также запуск сервера и бота возможен с помощью Dockerfile.

## Демонстрация
<div align="center"><img src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/617608ce-0f89-44dc-bc1f-77a1ebcb648f"/><br />Возможности администратора<br/><br/></div>
<div align="center"><img width="750" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/f77de9ec-9814-465c-9164-5e69fb9e308f"/><br />Форма просмотра заказа<br/><br/></div>
<div align="center"><img width="750" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/64f2e38c-9c18-491e-bfcc-81ff25546802"/><br />Возможность рассылки из админ-панели<br/><br/></div>
<div align="center"><img height="600" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/6415464e-fc4f-4fd2-a64f-a1b2f59883c5"/><img height="600" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/d2f045e1-d9c7-4dac-bc84-9844158f67e3"/><br/><img height="600" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/ec81230e-8bd2-4baa-bc40-a393e526f5f0"/><img height="600" src="https://github.com/k-derkach-uni/telegram-django-test/assets/122341934/5c6b0e0c-9796-4997-9057-2eaaf7d9141a"/><br />Скриншоты работы бота<br/><br/></div>

## Структура проекта
Структура каталогов и файлов проекта следующая:

```
- project/
  - bot/
    - __init__.py
    - admin.py
    - apps.py
    - handlers.py
    - models.py
    - main.py
    - management/
      - commands/
        - __init__.py
        - runbot.py
    
  - project/
    - __init__.py
    - asgi.py
    - settings.py
    - urls.py
    - wsgi.py
```



  
