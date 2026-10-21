FROM python:3.11-slim

WORKDIR /app

# Dépendances Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code backend
COPY backend/ ./backend/

# Frontend statique et templates
COPY frontend/ ./frontend/

ENV PYTHONPATH=/app/backend
ENV FLASK_APP=/app/backend/app.py

EXPOSE 5000

WORKDIR /app/backend
CMD ["python", "app.py"]
