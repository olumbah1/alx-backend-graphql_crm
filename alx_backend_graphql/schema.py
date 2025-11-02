import graphene
from datetime import datetime
from graphene_django import DjangoObjectType
from crm.models import Customer, Order, Product

# Type Definitions
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'created_at']

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_date', 'total_amount']

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock']

class UpdatedProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()

# Queries
class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = graphene.List(CustomerType)
    all_orders = graphene.List(OrderType)
    all_products = graphene.List(ProductType)
    orders = graphene.List(OrderType, order_date_after=graphene.String())
    
    def resolve_hello(self, info):
        return "Hello from GraphQL CRM!"
    
    def resolve_all_customers(self, info):
        return Customer.objects.all()
    
    def resolve_all_orders(self, info):
        return Order.objects.all()
    
    def resolve_all_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info, order_date_after=None):
        queryset = Order.objects.all()
        if order_date_after:
            try:
                date_filter = datetime.fromisoformat(order_date_after)
                queryset = queryset.filter(order_date__gte=date_filter)
            except ValueError:
                pass
        return queryset

# Mutations
class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(UpdatedProductType)
    
    class Arguments:
        pass
    
    def mutate(self, info):
        """
        Mutation to update low-stock products (stock < 10).
        Increments stock by 10 for each product found.
        Returns list of updated products with new stock levels.
        """
        try:
            low_stock_products = Product.objects.filter(stock__lt=10)
            updated_products = []
            
            for product in low_stock_products:
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

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)