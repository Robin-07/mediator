# Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /mediator

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application files
COPY ./mediator /mediator/mediator

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "mediator.main:app", "--host", "0.0.0.0", "--port", "8000"]
