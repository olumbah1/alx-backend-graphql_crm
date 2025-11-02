import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
from datetime import datetime
from crm.models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Output Types
class UpdatedProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            # Check if email already exists
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(
                    customer=None,
                    message="Email already exists",
                    success=False
                )

            # Create customer
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.get('phone', '')
            )
            customer.full_clean()  # Validates phone format
            customer.save()

            return CreateCustomer(
                customer=customer,
                message="Customer created successfully",
                success=True
            )

        except ValidationError as e:
            return CreateCustomer(
                customer=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateCustomer(
                customer=None,
                message=f"Error creating customer: {str(e)}",
                success=False
            )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success_count = graphene.Int()

    def mutate(self, info, input):
        customers = []
        errors = []

        for idx, customer_data in enumerate(input):
            try:
                # Check if email already exists
                if Customer.objects.filter(email=customer_data.email).exists():
                    errors.append(
                        f"Row {idx + 1}: Email '{customer_data.email}' already exists"
                    )
                    continue

                # Create customer
                customer = Customer(
                    name=customer_data.name,
                    email=customer_data.email,
                    phone=customer_data.get('phone', '')
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)

            except ValidationError as e:
                errors.append(f"Row {idx + 1}: {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx + 1}: Error - {str(e)}")

        return BulkCreateCustomers(
            customers=customers,
            errors=errors if errors else None,
            success_count=len(customers)
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            # Validate price
            if input.price <= 0:
                return CreateProduct(
                    product=None,
                    message="Price must be positive",
                    success=False
                )

            # Validate stock
            stock = input.get('stock', 0)
            if stock < 0:
                return CreateProduct(
                    product=None,
                    message="Stock cannot be negative",
                    success=False
                )

            # Create product
            product = Product(
                name=input.name,
                price=input.price,
                stock=stock
            )
            product.full_clean()
            product.save()

            return CreateProduct(
                product=product,
                message="Product created successfully",
                success=True
            )

        except ValidationError as e:
            return CreateProduct(
                product=None,
                message=str(e),
                success=False
            )
        except Exception as e:
            return CreateProduct(
                product=None,
                message=f"Error creating product: {str(e)}",
                success=False
            )


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()

    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                return CreateOrder(
                    order=None,
                    message=f"Customer with ID {input.customer_id} does not exist",
                    success=False
                )

            # Validate at least one product
            if not input.product_ids or len(input.product_ids) == 0:
                return CreateOrder(
                    order=None,
                    message="At least one product must be selected",
                    success=False
                )

            # Validate all products exist
            products = []
            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                except Product.DoesNotExist:
                    return CreateOrder(
                        order=None,
                        message=f"Product with ID {product_id} does not exist",
                        success=False
                    )

            # Create order in a transaction
            with transaction.atomic():
                order = Order(customer=customer)
                if hasattr(input, 'order_date') and input.order_date:
                    order.order_date = input.order_date
                order.save()

                # Add products
                order.products.set(products)

                # Calculate total amount
                total = sum(product.price for product in products)
                order.total_amount = total
                order.save()

            return CreateOrder(
                order=order,
                message="Order created successfully",
                success=True
            )

        except Exception as e:
            return CreateOrder(
                order=None,
                message=f"Error creating order: {str(e)}",
                success=False
            )


class UpdateLowStockProducts(graphene.Mutation):
    """Mutation to update low-stock products (stock < 10)"""
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(UpdatedProductType)
    
    class Arguments:
        pass
    
    def mutate(self, info):
        """
        Updates products with stock < 10 by incrementing stock by 10.
        Returns list of updated products with new stock levels.
        """
        try:
            # Find all products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            updated_products = []
            
            for product in low_stock_products:
                # Increment stock by 10 (simulate restocking)
                product.stock += 10
                product.save()
                
                updated_products.append(
                    UpdatedProductType(
                        id=product.id,
                        name=product.name,
                        stock=product.stock
                    )
                )
            
            return UpdateLowStockProducts(
                success=True,
                message=f"Successfully updated {len(updated_products)} products",
                updated_products=updated_products
            )
        
        except Exception as e:
            return UpdateLowStockProducts(
                success=False,
                message=f"Error updating low stock products: {str(e)}",
                updated_products=[]
            )


# Query with Filters
class Query(graphene.ObjectType):
    # Filtered queries using DjangoFilterConnectionField
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)
    
    # Legacy list queries (non-filtered, for backward compatibility)
    customers_list = graphene.List(
        CustomerType,
        name=graphene.String(),
        email=graphene.String(),
        phone_starts_with=graphene.String(),
        created_at_gte=graphene.DateTime(),
        created_at_lte=graphene.DateTime()
    )
    
    products_list = graphene.List(
        ProductType,
        name=graphene.String(),
        price_gte=graphene.Float(),
        price_lte=graphene.Float(),
        stock_gte=graphene.Int(),
        stock_lte=graphene.Int(),
        low_stock=graphene.Int()
    )
    
    orders_list = graphene.List(
        OrderType,
        customer_name=graphene.String(),
        customer_email=graphene.String(),
        product_name=graphene.String(),
        product_id=graphene.ID(),
        total_amount_gte=graphene.Float(),
        total_amount_lte=graphene.Float(),
        order_date_gte=graphene.DateTime(),
        order_date_lte=graphene.DateTime()
    )
    
    # Single item queries
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    
    # Hello field for heartbeat verification
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello from GraphQL CRM!"

    def resolve_customers_list(self, info, **kwargs):
        """Resolve customers with filters"""
        queryset = Customer.objects.all()
        
        # Apply filters
        if 'name' in kwargs:
            queryset = queryset.filter(name__icontains=kwargs['name'])
        if 'email' in kwargs:
            queryset = queryset.filter(email__icontains=kwargs['email'])
        if 'phone_starts_with' in kwargs:
            queryset = queryset.filter(phone__startswith=kwargs['phone_starts_with'])
        if 'created_at_gte' in kwargs:
            queryset = queryset.filter(created_at__gte=kwargs['created_at_gte'])
        if 'created_at_lte' in kwargs:
            queryset = queryset.filter(created_at__lte=kwargs['created_at_lte'])
        
        return queryset

    def resolve_products_list(self, info, **kwargs):
        """Resolve products with filters"""
        queryset = Product.objects.all()
        
        # Apply filters
        if 'name' in kwargs:
            queryset = queryset.filter(name__icontains=kwargs['name'])
        if 'price_gte' in kwargs:
            queryset = queryset.filter(price__gte=kwargs['price_gte'])
        if 'price_lte' in kwargs:
            queryset = queryset.filter(price__lte=kwargs['price_lte'])
        if 'stock_gte' in kwargs:
            queryset = queryset.filter(stock__gte=kwargs['stock_gte'])
        if 'stock_lte' in kwargs:
            queryset = queryset.filter(stock__lte=kwargs['stock_lte'])
        if 'low_stock' in kwargs:
            queryset = queryset.filter(stock__lt=kwargs['low_stock'])
        
        return queryset

    def resolve_orders_list(self, info, **kwargs):
        """Resolve orders with filters"""
        queryset = Order.objects.all()
        
        # Apply filters
        if 'customer_name' in kwargs:
            queryset = queryset.filter(customer__name__icontains=kwargs['customer_name'])
        if 'customer_email' in kwargs:
            queryset = queryset.filter(customer__email__icontains=kwargs['customer_email'])
        if 'product_name' in kwargs:
            queryset = queryset.filter(products__name__icontains=kwargs['product_name']).distinct()
        if 'product_id' in kwargs:
            queryset = queryset.filter(products__id=kwargs['product_id']).distinct()
        if 'total_amount_gte' in kwargs:
            queryset = queryset.filter(total_amount__gte=kwargs['total_amount_gte'])
        if 'total_amount_lte' in kwargs:
            queryset = queryset.filter(total_amount__lte=kwargs['total_amount_lte'])
        if 'order_date_gte' in kwargs:
            queryset = queryset.filter(order_date__gte=kwargs['order_date_gte'])
        if 'order_date_lte' in kwargs:
            queryset = queryset.filter(order_date__lte=kwargs['order_date_lte'])
        
        return queryset

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None


# Mutation
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)