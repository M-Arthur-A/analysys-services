# Внутренний корпоративный сайт
<!-- TOC start -->
- [BACKEND](#backend)
   - [STACK](#stack)
- [FRONTEND DEMO](#frontend-demo)
   - [ОБЩЕЕ](#fe-common)
   - [РОСРЕЕСТР](#fe-egrn)
   - [ЕФРСБ](#fe-efrsb)
<!-- TOC end -->

<!-- TOC --><a name="backend"></a>
## BACKEND
Бэкенд сайта позволяет заказывать выписки из РОСРЕЕСТРА (через подрядчика) и скачивать информацию по банкротным торгам с ЕФРСБ (скрапинг fedresurs.ru)
<!-- TOC --><a name="stack"></a>
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

<!-- TOC --><a name="frontend-demo"></a>
## FRONTEND DEMO
<!-- TOC --><a name="fe-common"></a>
### ОБЩЕЕ
![auth](media/auth.png "authentication")
![error](media/error.png "error example")
<!-- TOC --><a name="fe-egrn"></a>
### РОСРЕЕСТР
![egrn-list](media/egrn-list.png "egrn list")
![egrn-item](media/egrn-item.png "egrn item")
![egrn-add](media/egrn-add.png "egrn add")
<!-- TOC --><a name="fe-efrsb"></a>
### ЕФРСБ
![efrsb](media/efrsb.png "efrsb")
