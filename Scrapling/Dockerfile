FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
# Scrapling tiene los requerimientos en scripts/
COPY scripts/requirements.txt ./scripts/requirements.txt
RUN pip install --no-cache-dir -r scripts/requirements.txt
COPY . .
CMD ["python", "scripts/limpiar_csv.py"]