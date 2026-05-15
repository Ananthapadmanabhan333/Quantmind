FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]