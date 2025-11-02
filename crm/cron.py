from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

GRAPHQL_URL = "http://localhost:8000/graphql"
HEARTBEAT_LOG = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM is alive.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    """
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    heartbeat_msg = f"{timestamp} CRM is alive\n"
    
    try:
        # Append to heartbeat log
        with open(HEARTBEAT_LOG, 'a') as f:
            f.write(heartbeat_msg)
        
        # Optional: Query GraphQL hello field to verify endpoint is responsive
        try:
            transport = RequestsHTTPTransport(url=GRAPHQL_URL)
            client = Client(transport=transport, fetch_schema_from_transport=False)
            
            query = gql("""
                query {
                    hello
                }
            """)
            
            result = client.execute(query)
            if result.get('hello'):
                print(f"[Heartbeat] {heartbeat_msg.strip()} - GraphQL endpoint responsive")
        except Exception as e:
            print(f"[Heartbeat] GraphQL query failed: {e}")
    
    except Exception as e:
        print(f"Error logging heartbeat: {e}")
        

def update_low_stock():
    """
    Execute GraphQL mutation to update low-stock products every 12 hours.
    Updates products with stock < 10 by incrementing stock by 10.
    Logs updated product names and new stock levels to /tmp/low_stock_updates_log.txt
    """
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
    from datetime import datetime
    
    GRAPHQL_URL = "http://localhost:8000/graphql"
    LOG_FILE = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        transport = RequestsHTTPTransport(url=GRAPHQL_URL)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        result = client.execute(mutation)
        
        # Log the results
        with open(LOG_FILE, 'a') as f:
            if result.get('updateLowStockProducts', {}).get('success'):
                f.write(f"[{timestamp}] Low stock update executed successfully\n")
                for product in result.get('updateLowStockProducts', {}).get('updatedProducts', []):
                    product_name = product.get('name', 'Unknown')
                    new_stock = product.get('stock', 'N/A')
                    f.write(f"[{timestamp}] Product: {product_name}, New Stock Level: {new_stock}\n")
            else:
                message = result.get('updateLowStockProducts', {}).get('message', 'Unknown error')
                f.write(f"[{timestamp}] Low stock update failed: {message}\n")
    
    except Exception as e:
        print(f"Error updating low stock products: {e}")
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{timestamp}] Error: {str(e)}\n")