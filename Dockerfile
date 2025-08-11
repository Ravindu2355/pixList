FROM python:3.9-slim

# Prevent Python from writing .pyc files & buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better build cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port if Flask is serving something
EXPOSE 8000

# Start both Flask and the bot
# Using bash -c so both run in one container
CMD ["bash", "-c", "gunicorn --bind 0.0.0.0:8000 flask_server:app & python3 main.py"]
