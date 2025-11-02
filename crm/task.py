from celery import shared_task
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://localhost:8000/graphql"
REPORT_LOG = "/tmp/crm_report_log.txt"


@shared_task
def generate_crm_report():
    """
    Celery task to generate a weekly CRM report.
    Fetches total customers, orders, and revenue via GraphQL.
    Logs report to /tmp/crm_report_log.txt with timestamp.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Query GraphQL endpoint for CRM stats
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        query = gql("""
            query {
                customersList {
                    id
                }
                ordersList {
                    id
                    totalAmount
                }
            }
        """)
        
        result = client.execute(query)
        
        # Extract data
        customers = result.get('customersList', [])
        orders = result.get('ordersList', [])
        
        total_customers = len(customers)
        total_orders = len(orders)
        total_revenue = sum(
            float(order.get('totalAmount', 0)) 
            for order in orders
        )
        
        # Format and log report
        report_msg = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue.\n"
        
        with open(REPORT_LOG, 'a') as f:
            f.write(report_msg)
        
        print(f"CRM Report generated: {report_msg.strip()}")
        return {
            'status': 'success',
            'customers': total_customers,
            'orders': total_orders,
            'revenue': total_revenue
        }
    
    except Exception as e:
        error_msg = f"{timestamp} - Error generating report: {str(e)}\n"
        with open(REPORT_LOG, 'a') as f:
            f.write(error_msg)
        print(f"Error: {error_msg.strip()}")
        return {
            'status': 'error',
            'message': str(e)
        }