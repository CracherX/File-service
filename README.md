
# FileService — Тестовое задание

Это тестовое задание — веб-приложение для управления файловым хранилищем.

---

## Описание

Приложение позволяет загружать, получать, обновлять, удалять и скачивать файлы.  
Доступна автоматическая документация по маршрутам API — перейти можно по адресу:

```
/docs
```

---

## Запуск приложения

### Через Docker Compose

```bash
docker-compose up --build
```

Это запустит сервис с необходимой базой данных и приложением.

---

### Без Docker

1. Убедитесь, что у вас установлен Python 3.10+.
2. Создайте и настройте базу данных согласно конфигу.
3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Запустите приложение:

```bash
uvicorn app.main:app --reload
```

---

## Конфигурация

```env
# App
APP_NAME=FileService
LOG_LEVEL=DEBUG
UPLOAD_DIR=uploads

# Database
DB=Test
DB_USER=Test
DB_PASSWORD=Test
DB_HOST=db
DB_PORT=5432
DB_ENGINE=postgresql
```

---

## Основные маршруты API

### Получить список файлов

```
GET /files
```

- Возвращает список файлов с пагинацией и фильтрацией по пути.
- Параметры запроса:

| Параметр  | Тип    | Описание                   | По умолчанию |
|-----------|--------|----------------------------|--------------|
| page      | int    | Номер страницы             | 1            |
| page_size | int    | Размер страницы            | 20           |
| path      | string | Фильтр по пути файлов      | отсутствует  |

---

### Получить файл по ID

```
GET /file?id={id}
```

- Возвращает информацию о файле по его ID.

---

### Удалить файл

```
DELETE /file?id={id}
```

- Удаляет файл по ID.
- Возвращает 404, если файл не найден.

---

### Обновить данные файла

```
PATCH /file
```

- Обновляет название, путь и/или комментарий к файлу, а так же расположение файла в хранилище.
- В теле запроса передаются поля:

```json
{
  "id": 123,
  "name": "new_name",
  "path": "/new/path",
  "comment": "new comment"
}
```

- Возвращает 404, если файл не найден.

---

### Загрузить файл

```
POST /file
```
- form-data
- Загружает файл с метаданными.
- Параметры формы:

| Параметр | Описание               | Обязательный |
|----------|------------------------|--------------|
| upload   | Файл                   | Да           |
| path     | Путь для файла         | Да           |
| comment  | Комментарий к файлу    | Нет          |

---

### Скачать файл

```
GET /file/{file_id}/download
```

- Скачивает файл по ID.
- Возвращает бинарные данные.
- 404 если файл не найден.

---

### Актуализировать файлы

```
POST /files/actualize
```

- Синхронизирует файлы между хранилищем и базой данных.
- Возвращает статистику по добавленным, удалённым и общему количеству файлов.

---

## DTO — структуры запросов

- `GetFilesList`: параметры для получения списка файлов (page, page_size, path).
- `GetFile`: ID файла.
- `UploadFile`: данные для загрузки файла (имя, расширение, размер, путь, комментарий).
- `DeleteFile`: ID файла.
- `UpdateFile`: данные для обновления файла (ID, имя, путь, комментарий).

---

## DTO — структуры ответов

- `FileDTO`: информация о файле (id, имя, расширение, размер, путь, даты создания и обновления, комментарий).
- `DownloadFileDTO`: данные для скачивания файла (путь, имя файла).
- `ActualizeResultDTO`: результат синхронизации (добавленные, удалённые, всего в БД).

---

