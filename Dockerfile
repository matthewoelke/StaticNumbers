FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mount point for the SQLite database (override DATABASE_PATH to use a different location)
VOLUME ["/data"]

ENV DATABASE_PATH=/data/numbers.db
ENV SECRET_KEY=change-this-before-deploying

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
