# 🚀 Krishi Mitra Deployment Guide

Complete guide for deploying Krishi Mitra to production.

## 📋 Pre-Deployment Checklist

- [ ] All tests passing locally
- [ ] Environment variables configured
- [ ] Database backups configured
- [ ] API keys secured
- [ ] CORS origins updated
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] SSL certificates ready

## 🐳 Docker Deployment

### 1. Create Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/rag/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=${MONGO_URL}
      - SECRET_KEY=${SECRET_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - mongodb
    restart: unless-stopped
    volumes:
      - ./backend:/app
    networks:
      - krishi-network

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped
    networks:
      - krishi-network

volumes:
  mongodb_data:

networks:
  krishi-network:
    driver: bridge
```

### 3. Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment Options

### Option 1: AWS (Recommended)

#### Using AWS ECS + Fargate

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name krishi-mitra-backend
```

2. **Build and Push Image**
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t krishi-mitra-backend ./backend

# Tag image
docker tag krishi-mitra-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/krishi-mitra-backend:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/krishi-mitra-backend:latest
```

3. **Create ECS Task Definition**
```json
{
  "family": "krishi-mitra-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/krishi-mitra-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "LOG_LEVEL", "value": "WARNING"}
      ],
      "secrets": [
        {"name": "MONGO_URL", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "PINECONE_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "GEMINI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ]
    }
  ]
}
```

4. **Create ECS Service**
```bash
aws ecs create-service \
  --cluster krishi-mitra-cluster \
  --service-name backend-service \
  --task-definition krishi-mitra-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

#### Using AWS Lambda (Serverless)

1. **Install Mangum**
```bash
pip install mangum
```

2. **Update main.py**
```python
from mangum import Mangum

# ... existing code ...

# Add Lambda handler
handler = Mangum(app)
```

3. **Deploy with AWS SAM**
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  KrishiMitraFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: backend/
      Handler: main.handler
      Runtime: python3.9
      MemorySize: 2048
      Timeout: 30
      Environment:
        Variables:
          PINECONE_API_KEY: !Ref PineconeApiKey
          GEMINI_API_KEY: !Ref GeminiApiKey
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

### Option 2: Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/krishi-mitra-backend

# Deploy to Cloud Run
gcloud run deploy krishi-mitra-backend \
  --image gcr.io/PROJECT_ID/krishi-mitra-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars PINECONE_API_KEY=$PINECONE_API_KEY,GEMINI_API_KEY=$GEMINI_API_KEY
```

### Option 3: Azure

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name krishi-mitra-rg --location eastus

# Create container
az container create \
  --resource-group krishi-mitra-rg \
  --name krishi-mitra-backend \
  --image <registry>/krishi-mitra-backend:latest \
  --dns-name-label krishi-mitra \
  --ports 8000 \
  --environment-variables \
    PINECONE_API_KEY=$PINECONE_API_KEY \
    GEMINI_API_KEY=$GEMINI_API_KEY
```

### Option 4: DigitalOcean App Platform

1. **Create app.yaml**
```yaml
name: krishi-mitra
services:
  - name: backend
    github:
      repo: your-username/krishi-mitra
      branch: main
      deploy_on_push: true
    dockerfile_path: backend/Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: professional-xs
    envs:
      - key: PINECONE_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: GEMINI_API_KEY
        scope: RUN_TIME
        type: SECRET
```

2. **Deploy**
```bash
doctl apps create --spec app.yaml
```

## 🔒 Security Hardening

### 1. Environment Variables

Use secrets management:

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name krishi-mitra/prod/api-keys \
  --secret-string '{"PINECONE_API_KEY":"xxx","GEMINI_API_KEY":"xxx"}'
```

**HashiCorp Vault:**
```bash
vault kv put secret/krishi-mitra \
  pinecone_api_key="xxx" \
  gemini_api_key="xxx"
```

### 2. Update CORS

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Enable HTTPS

**Using Nginx:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Rate Limiting

Install slowapi:
```bash
pip install slowapi
```

Update main.py:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/rag/query")
@limiter.limit("10/minute")
async def query_endpoint(request: Request, query: QueryRequest):
    # ... existing code ...
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

**Using Sentry:**
```bash
pip install sentry-sdk
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

**Using New Relic:**
```bash
pip install newrelic
newrelic-admin run-program uvicorn main:app
```

### 2. Logging

**CloudWatch (AWS):**
```python
import watchtower
import logging

logger = logging.getLogger(__name__)
logger.addHandler(watchtower.CloudWatchLogHandler())
```

**Google Cloud Logging:**
```python
from google.cloud import logging as gcp_logging

client = gcp_logging.Client()
client.setup_logging()
```

### 3. Metrics

**Prometheus:**
```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: krishi-mitra-backend
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG ./backend
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster krishi-mitra-cluster \
            --service backend-service \
            --force-new-deployment
```

## 🧪 Production Testing

```bash
# Health check
curl https://api.yourdomain.com/api/v1/rag/health

# Load testing with Apache Bench
ab -n 1000 -c 10 https://api.yourdomain.com/

# Load testing with Locust
pip install locust
locust -f load_test.py --host https://api.yourdomain.com
```

## 📈 Scaling Strategies

1. **Horizontal Scaling**: Add more instances
2. **Vertical Scaling**: Increase instance size
3. **Caching**: Redis for frequent queries
4. **CDN**: CloudFront/Cloudflare for static assets
5. **Database**: MongoDB Atlas with auto-scaling

## 🆘 Rollback Plan

```bash
# AWS ECS
aws ecs update-service \
  --cluster krishi-mitra-cluster \
  --service backend-service \
  --task-definition krishi-mitra-backend:PREVIOUS_VERSION

# Docker
docker-compose down
docker-compose up -d --build
```

---

**Deployment Complete! 🎉**

Your Krishi Mitra backend is now running in production.
