# SmartFridge: 1518 CHUPEP-8
Репозиторий, содержащий исходный код бэкенда команды "1518 CHUPEP-8" для Московской Предпрофессиональной олимпиады **Кейс №2 «SmartFridge: QR Control & IoT Sync»**.

### **Вы также можете ознакомиться с функционалом API, перейдя на https://api.saslo.shop/docs.**

## Инструкция по установке / развёртыванию
1. Скачайте и установите PostgreSQL [с официального сайта](https://www.postgresql.org/download/).
2. Настройка бд в командной строке (powershell):
```shell
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -U postgres
Вводим пароль пользователя postgres, который указывали при установке
CREATE ROLE root WITH LOGIN PASSWORD '1111' SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS;
CREATE DATABASE smartfridge;
```
3. Клонируем данный репозиторий
4. В файле .env укажите конфигурацию:

| Ключ | Описание | Значение |
|---|---|---|
| `DB_PASSWORD` | Пароль от пользователя `root` БД | **1111** |
5. Настройка пакетов и запуск. Убедитесь, что база данных запущена (простейший способ это сделать - запустить pgAdmin в меню Пуск и подключиться к локальной БД, которую мы настроили, указав пароль пользователя postgres)
```shell
python -m venv venv
.\venv\Scripts\Activate.ps1 (в зависимости от оболочки командной строки)
pip install -r .\requirements.txt
fastapi dev main.py
```