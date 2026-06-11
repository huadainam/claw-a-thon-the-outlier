FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copies source + the bundled seed/ cache (.dockerignore excludes .env, data/, tests/)
COPY . .

EXPOSE 8080

# Bootstraps seed/ into the live store, then serves dashboard + API + hourly scheduler
CMD ["python", "app.py", "--serve"]
