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

Контроллер устройств
======
Выступает вебсокет-сервером для обмена с устройствами, подключенными по сети. Работает с весами и принтерами этикеток. 
Клиент отправляет команды в формате:
`python client.py <mode> <ip> <port> <driver>`

Настроенные драйверы весов: 
1. Тензо-М - совместим с терминалом ТВ-020
2. Mettler-Toledo MTSics Level 1 - совместим с терминалом IND226
3. DIGI - совместим с терминалом DI160 (работает в потоке)

Настроенные драйверы принтеров:
1. Язык DPL - совместим с Datamax I-4212e

Симуляция весов
------
Для симуляции работы весов:

1. Запустите сервер в первом терминале.
2. В файле `scales/simulators.py` заполните адрес и порт виртуальных весов, укажите диапазон веса для генерации случайных значений. 
3. Запустите `scales/simulators.py` во втором терминале
4. Запустить тестовый клиент `client.py` в третьем терминале  
5. Весы будут бесконечно отвечать на запросы. Текст запроса не обрабатывается, на любую команду симулятор отвечает случайным значением веса. 

Настроенные команды DPL
------
Настроена обработка следующих команд для принтера этикеток:

1. Загрузка шрифта - команда формируется указанием пути до ttf-файла и номера, который нужно присвоить шрифту. Пример:
`COMMAND = build_dpl_ttf_upload_commands('devices/printers/fonts/opensans.ttf', '55')`

2. Загрузка картинки - команда формируется указанием пути до jpg/png-файла и имени, который нужно присвоить картинке. Пример:
`COMMAND = build_dpl_image_upload_commands("devices/printers/images/eac.jpg", image_name="eac")`

3. Отправка команды печати этикетки. Отправляется клиентом с указанием контрольных кодов типа <STX> и <CR>, которые корректно кодируются перед отправкой. 
```
data = (
    "<STX>yUUC<CR>"
    "<STX>L<CR>"
    "4911u6601000100P015P009Тестовый текст шрифтом Oswald: абвгдеёжзикл...уфцчщьъэюя123()_\"\"<CR>"
    "4911u7701000200P015P009Тестовый EAN13:<CR>"
    "4F00" + "070" + "01000350" + "012345678901<CR>"
    "4911u7705000200P015P009Тестовый GS1 DataMatrix:<CR>"
    "4W1c00" + "000" + "05000400" + "2000" + "000000" + "<FNC1>" + "0104603934000793215?ZjQDTZ4NBNy<GS>93zFAP<CR>"
    "4911u5501000500P015P009Тестовая картинка:<CR>"
    "1Y00" + "000" + "05000500" + "vilka<CR>"
    "E<CR>"
)
COMMAND = build_dpl_unicode_label(data)
```