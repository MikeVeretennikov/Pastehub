# PasteHub


# Инструкция по запуску проекта

### Подготовка виртуального окружения

```shell
python3 -m venv venv
source venv/bin/activate
```

### Установка зависимостей:

```shell
pip install -r requirements/prod.txt
```

<details>
<summary>Для среды dev и test</summary>

Для dev-среды

```shell
pip install -r requirements/dev.txt
```

Для test-среды

```shell
pip install -r requirements/test.txt
```

</details>

### Конфигурация переменных окружения

Переименуйте (скопируйте) файл `config.env` в `.env` и, при необходимости, отредактируйте значения переменных

```shell
cp config.env .env
```

<details>
<summary>dev-среда</summary>

Для dev-среды установите `true` для переменной `DJANGO_DEBUG`

</details>

### Применение миграций:

```shell
cd lyceum
python manage.py migrate
```

### Сборка статики:

```shell
python manage.py collectstatic
```

### Компиляция переводов:

```shell
python manage.py compilemessages
```

### Запуск приложения:

```shell
python manage.py runserver
```

<details>
<summary>Запуск тестов</summary>

```shell
python manage.py test
```

(Должны быть установленные зависимости для тестов)

</details>

