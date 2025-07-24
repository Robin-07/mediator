# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application and startup script
COPY ./mediator /app/mediator
COPY ./scripts/start.sh /app/start.sh

# Make script executable
RUN chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]
