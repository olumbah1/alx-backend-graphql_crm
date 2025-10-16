import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order
from decimal import Decimal


def seed_database():
    print("Seeding database...")

    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()
    print("Cleared existing data")

    # Create Customers
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Williams", "email": "carol@example.com", "phone": "+9876543210"},
        {"name": "David Brown", "email": "david@example.com", "phone": "987-654-3210"},
        {"name": "Eve Davis", "email": "eve@example.com", "phone": "+1122334455"},
    ]

    customers = []
    for data in customers_data:
        customer = Customer.objects.create(**data)
        customers.append(customer)
        print(f"Created customer: {customer.name}")

    # Create Products
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Mouse", "price": Decimal("29.99"), "stock": 50},
        {"name": "Keyboard", "price": Decimal("79.99"), "stock": 30},
        {"name": "Monitor", "price": Decimal("299.99"), "stock": 15},
        {"name": "Headphones", "price": Decimal("149.99"), "stock": 25},
        {"name": "Webcam", "price": Decimal("89.99"), "stock": 20},
        {"name": "USB Cable", "price": Decimal("9.99"), "stock": 100},
    ]

    products = []
    for data in products_data:
        product = Product.objects.create(**data)
        products.append(product)
        print(f"Created product: {product.name} - ${product.price}")

    # Create Orders
    orders_data = [
        {"customer": customers[0], "products": [products[0], products[1], products[2]]},
        {"customer": customers[1], "products": [products[3], products[4]]},
        {"customer": customers[2], "products": [products[1], products[6]]},
        {"customer": customers[3], "products": [products[0], products[3], products[4], products[5]]},
        {"customer": customers[4], "products": [products[2], products[6]]},
    ]

    for idx, order_data in enumerate(orders_data):
        order = Order.objects.create(customer=order_data["customer"])
        order.products.set(order_data["products"])
        order.calculate_total()
        print(f"Created order #{order.id} for {order.customer.name} - Total: ${order.total_amount}")

    print("\nDatabase seeded successfully!")
    print(f"- {Customer.objects.count()} customers")
    print(f"- {Product.objects.count()} products")
    print(f"- {Order.objects.count()} orders")


if __name__ == "__main__":
    seed_database()