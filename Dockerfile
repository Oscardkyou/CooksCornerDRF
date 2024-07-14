# Используйте мультистадийную сборку для оптимизации размера образа
# Стадия сборки
FROM python:3.8 AS builder
WORKDIR /app
COPY requirements.txt ./
# Установка зависимостей в папку /app/wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Финальная стадия
FROM python:3.8-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
# Установка зависимостей из локальных wheel-файлов
RUN pip install --no-cache /wheels/*
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "cookscorner.wsgi:application"]