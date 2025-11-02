# CRM Application Setup and Celery Configuration

## Prerequisites

Before running the CRM application with Celery, ensure you have the following installed:

- Python 3.8+
- Django 4.2.0
- PostgreSQL or SQLite (for database)
- Redis (for Celery broker and result backend)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Redis

**On macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**On Windows:**
Download Redis from: https://github.com/microsoftarchive/redis/releases

Or use Docker:
```bash
docker run -d -p 6379:6379 redis:latest
```

### 3. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

## Django Setup

### 1. Run Migrations

```bash
python manage.py migrate
```

### 2. Create Celery Beat Schedule (Optional)

```bash
python manage.py shell
from django_celery_beat.models import PeriodicTask, CrontabSchedule
# The schedule is already configured in settings.py
exit()
```

## Running the Application

### Terminal 1: Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at: `http://localhost:8000/graphql`

### Terminal 2: Celery Worker

```bash
celery -A alx_backend_graphql worker -l info
```

### Terminal 3: Celery Beat (Task Scheduler)

```bash
celery -A alx_backend_graphql beat -l info
```

## Celery Tasks

### Generate CRM Report

**Task Name:** `crm.tasks.generate_crm_report`

**Schedule:** Every Monday at 6:00 AM UTC

**What it does:**
- Queries the GraphQL endpoint for total customers, orders, and revenue
- Logs a formatted report to `/tmp/crm_report_log.txt`
- Returns task status (success or error)

### Manual Task Execution

To manually trigger the report generation:

```bash
python manage.py shell
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
exit()
```

## Monitoring and Logs

### View Celery Task Logs

Check the terminal where Celery worker is running for real-time logs.

### View Generated Reports

```bash
cat /tmp/crm_report_log.txt
```

### Monitor Celery Tasks

```bash
celery -A alx_backend_graphql events
```

Or use Flower (web-based monitoring):

```bash
pip install flower
celery -A alx_backend_graphql flower
# Access at http://localhost:5555
```

## Troubleshooting

### Redis Connection Error

**Problem:** `ConnectionError: Error 111 connecting to localhost:6379`

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start Redis
redis-server
```

### Celery Task Not Executing

**Problem:** Tasks scheduled but not running

**Solution:**
1. Ensure Celery Beat is running in a separate terminal
2. Check Celery Beat logs for errors
3. Verify Redis connection: `redis-cli ping`

### GraphQL Query Error

**Problem:** `Error generating report: HTTPConnectionError`

**Solution:**
1. Ensure Django server is running on `http://localhost:8000`
2. Check if GraphQL schema is properly configured
3. Verify `customersList` and `ordersList` queries exist in schema

## Configuration Reference

### settings.py Celery Configuration

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### Celery Beat Schedule

```python
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week=0, hour=6, minute=0),
    },
}
```

- `day_of_week=0` = Monday
- `hour=6` = 6:00 AM
- `minute=0` = 0 minutes

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django-Celery-Beat Documentation](https://github.com/celery/django-celery-beat)
- [GraphQL Schema](./schema.py)