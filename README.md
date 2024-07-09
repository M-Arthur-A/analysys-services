# Внутренний корпоративный сайт
## BACKEND
Бэкенд сайта позволяет заказывать выписки из РОСРЕЕСТРА (через подрядчика) и скачивать информацию по банкротным торгам с ЕФРСБ (скрапинг fedresurs.ru)
### STACK
#### Общее
- python
- loguru
- celery
- pandas

#### WEB
- fastapi
- gunicorn
- sqladmin

#### Базы данных
- sqlalchemy
- alembic
- redis

#### Скрапинг
- scrapy
- aiohttp

## FRONTEND DEMO
### ОБЩЕЕ
![auth](media/auth.png "authentication")
![error](media/error.png "error example")
### РОСРЕЕСТР
![egrn-list](media/egrn-list.png "egrn list")
![egrn-item](media/egrn-item.png "egrn item")
![egrn-add](media/egrn-add.png "egrn add")
### ЕФРСБ
![efrsb](media/efrsb.png "efrsb")

