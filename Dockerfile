# Используйте официальный образ Python как родительский образ
FROM python:3.8

# Установите рабочий каталог в контейнере
WORKDIR /app

# Используйте переменные среды во время сборки
ARG RAILWAY_SERVICE_NAME

# Копируйте файлы зависимостей и установите их, используя кэш
COPY requirements.txt ./
RUN --mount=type=cache,id=s/<service id>-/root/cache/pip,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

# Копируйте остальную часть вашего кода приложения
COPY . .

# Запустите сервер приложения
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "cookscorner.wsgi:application"]