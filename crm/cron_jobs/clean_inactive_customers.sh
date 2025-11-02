#!/bin/bash

# Script to clean up inactive customers with no orders in the past year
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Execute Django command to delete inactive customers
DELETED_COUNT=$(cd /path/to/alx-backend-graphql_crm && python manage.py shell << EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find and delete customers with no orders since a year ago
deleted_customers = Customer.objects.filter(
    orders__isnull=True,
    created_at__lt=one_year_ago
).delete()

# count of deleted customers
count = deleted_customers[0]
print(count)
EOF
)

# Log the results with count
echo "[$TIMESTAMP] Deleted count: $DELETED_COUNT inactive customers" >> "$LOG_FILE"