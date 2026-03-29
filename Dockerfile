FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Optional: collect static files (only if using static)
# RUN python manage.py collectstatic --noinput

# Cloud Run uses PORT=8080 automatically
CMD ["sh", "-c", "gunicorn aeroload_inspector.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 300"]