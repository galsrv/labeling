About
======
This is a pet project targeted mostly to master FastAPI framework. Side goals - to build Telegram bot and its admin panel frontend.  

Stack
======
* Python 3.12
* Backend - FastAPI & SQLAlchemy & Alembic
* Frontend - Nicegui
* Bot - Aiogram
* Common elements - Pydantic & Pydantic Settings & Loguru

Architecture
======
<p align="center">
    <img src="infra/arc.png" height="500">
</p>

Deployment
======
Local deployment
------
There are 3 separate applications to be installed - backend, frontend and bot.

1. Create and activate virtual environment
```shell
python3.12 -m venv venv
. venv/bin/activate
```