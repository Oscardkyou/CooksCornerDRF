# Используйте официальный образ Python как базовый
FROM python:3.11.1

# Установите рабочий каталог в контейнере
ENV APP_HOME /app
WORKDIR $APP_HOME

# Скопируйте файл зависимостей и установите зависимости
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Скопируйте локальный код в контейнер
COPY . .

# Дайте права на выполнение скрипту entrypoint.sh
RUN chmod +x ./entrypoint.sh

# Запустите скрипт при старте контейнера
CMD ["./entrypoint.sh"]
