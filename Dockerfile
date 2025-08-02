FROM python:3.9-alpine

WORKDIR /app

# Устанавливаем только необходимые зависимости
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    && python -m venv /venv \
    && apk del .build-deps

ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME /app

# Очистка кеша pip
RUN find /venv -type d -name '__pycache__' -exec rm -rf {} +

CMD ["python", "core/bot.py"]