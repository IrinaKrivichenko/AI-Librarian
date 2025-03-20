# Используем базовый образ с Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей requirements.txt в контейнер
COPY requirements.txt .

# Устанавливаем зависимости, используя legacy-resolver
RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Указываем команду, которая будет запускаться внутри контейнера
CMD ["python", "run_gradio_interface.py"]
