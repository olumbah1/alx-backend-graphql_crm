#!/usr/bin/env python
import sys
import os
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add project to path
sys.path.insert(0, '/path/to/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

import django
django.setup()

# GraphQL endpoint configuration
GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

def get_pending_orders():
    """Query GraphQL endpoint for orders from the last 7 days"""
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Calculate date 7 days ago
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        query = gql("""
            query {
                orders(orderDateAfter: "%s") {
                    id
                    orderDate
                    customer {
                        id
                        email
                    }
                }
            }
        """ % seven_days_ago)
        
        result = client.execute(query)
        return result.get('orders', [])
    
    except Exception as e:
        print(f"Error querying GraphQL endpoint: {e}")
        return []

def log_order_reminders(orders):
    """Log order reminders with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(LOG_FILE, 'a') as f:
        for order in orders:
            customer_email = order.get('customer', {}).get('email', 'N/A')
            order_id = order.get('id', 'N/A')
            log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
            f.write(log_entry)

def main():
    """Main function to process order reminders"""
    try:
        orders = get_pending_orders()
        log_order_reminders(orders)
        print("Order reminders processed!")
    except Exception as e:
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()