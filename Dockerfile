FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y procps

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "sleep 5 && python manage.py migrate && gunicorn aeroload_inspector.wsgi:application --bind 0.0.0.0:8000 --workers 2"]