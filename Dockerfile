# Используйте официальный образ Python как родительский образ
FROM python:3.8

# Установите рабочий каталог в контейнере
WORKDIR /app

# Копируйте файлы зависимостей и установите их
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Копируйте остальную часть вашего кода приложения
COPY . .

# Запустите сервер приложения
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "cookscorner.wsgi:application"]