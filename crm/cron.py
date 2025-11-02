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