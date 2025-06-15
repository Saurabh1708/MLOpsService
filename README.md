# MLOps Platform

A hypervisor-like service for managing ML deployments with intelligent scheduling.

## Features

- User authentication and organization management
- Cluster resource management
- Intelligent deployment scheduling with priority-based preemption
- Real-time monitoring and metrics
- Docker container deployment support

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15
- Redis 7

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd MLOpsService
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the services using Docker Compose:

```bash
docker-compose up -d
```

## API Endpoints

### Authentication

- POST `/auth/register` - Register a new user
- POST `/auth/login` - Login and get access token

### Organizations

- POST `/organizations` - Create a new organization
- GET `/organizations/me` - Get current user's organization

### Clusters

- POST `/clusters` - Create a new cluster
- GET `/clusters` - List available clusters

### Deployments

- POST `/deployments` - Create a new deployment
- GET `/deployments` - List user's deployments
- GET `/deployments/{id}` - Get deployment details
- DELETE `/deployments/{id}` - Cancel a deployment

### Monitoring

- GET `/monitoring/health` - Health check endpoint
- GET `/monitoring/metrics` - Get system metrics

## Development

### Project Structure

```
app/
├── api/
│   ├── endpoints/
│   │   ├── auth.py
│   │   ├── clusters.py
│   │   ├── deployments.py
│   │   ├── monitoring.py
│   │   └── organizations.py
│   └── deps.py
├── core/
│   ├── config.py
│   ├── enums.py
│   └── security.py
├── db/
│   └── base.py
├── models/
│   ├── user.py
│   ├── organization.py
│   ├── cluster.py
│   └── deployment.py
├── schemas/
│   ├── user.py
│   ├── organization.py
│   ├── cluster.py
│   └── deployment.py
├── services/
│   └── scheduler.py
├── utils/
│   └── invite.py
└── main.py
```

# Database Schema

```mermaid
erDiagram
    Organization ||--o{ User : "has"
    Organization ||--o{ Cluster : "owns"
    User ||--o{ Cluster : "owns"
    User ||--o{ Deployment : "creates"
    Cluster ||--o{ Deployment : "hosts"
    Deployment ||--o{ MonitoringMetrics : "has"

    Organization {
        int id PK
        string name
        string invite_code
        datetime created_at
        boolean is_active
    }

    User {
        int id PK
        string username
        string email
        string password_hash
        int organization_id FK
        datetime created_at
        boolean is_active
    }

    Cluster {
        int id PK
        string name
        int organization_id FK
        int owner_id FK
        float total_ram_gb
        int total_cpu_cores
        int total_gpu_count
        float available_ram_gb
        int available_cpu_cores
        int available_gpu_count
        datetime created_at
        boolean is_active
    }

    Deployment {
        int id PK
        string name
        int user_id FK
        int cluster_id FK
        string docker_image
        float required_ram_gb
        int required_cpu_cores
        int required_gpu_count
        enum priority
        enum status
        datetime created_at
        datetime scheduled_at
        datetime started_at
        datetime completed_at
        json meta_data
    }

    MonitoringMetrics {
        int id PK
        int deployment_id FK
        string metric_name
        float metric_value
        datetime timestamp
    }
```

### Running Tests

```bash
pytest
```

## License

MIT License
