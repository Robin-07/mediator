# Mediator

An async-first, FastAPI-based microservice that queues and processes media generation jobs using a mocked Replicate API. It utilizes Celery for background task management, PostgreSQL for job tracking, RabbitMQ as the message broker, and S3 storage for file uploads.

## Tech Stack

- **FastAPI** – API layer
- **Celery** – Async task processing
- **RabbitMQ** – Message broker
- **PostgreSQL** – Database
- **S3 (via boto3)** – Cloud Object Storage
- **Docker Compose** – Containerization/Deployments

## Architecture

```mermaid
flowchart LR

A((Mediator API))
B[(PostgreSQL)]
C(RabbitMQ)
D(Celery)
E[(S3 Bucket)]
F(Client)
G((Mocked Replicate API))

F -->|Generation Requests| A
A -->|Queue Tasks| C --> D
A -->|Persist Job Metadata| B
D --->|Submit Jobs| G
G -->|Webhooks| A
D -->|Upload Media Files| E

```

## Getting Started

#### 1. Clone this Repository
```bash
git clone https://github.com/Robin-07/mediator
cd mediator
```
#### 2. Create `.env` file at project root
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/postgres
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

# AWS settings
AWS_ACCESS_KEY_ID=AKIAVR****
AWS_SECRET_ACCESS_KEY=5/WNM24++BDWy****
AWS_REGION=us-east-1
S3_BUCKET_NAME=media-generations

# Application settings
DUMMY_IMAGE_URL=https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/1200px-Cat_November_2010-1a.jpg
REPLICATE_PREDICTIONS_MOCK_URL=http://mediator:8000/api/v1/predictions
REPLICATE_MODEL_VERSION=test-model
REPLICATE_CALLBACK_URL=http://mediator:8000/api/v1/callback
DEBUG=1
```

#### 3. Build and start the services
```bash
docker compose up --build
```

### Todo
- Use actual Replicate API
- Add rate limiting & robust retry logic
- Add webhook validation
- Add more unit & integration tests
- Add Prometheus/Grafana for metrics