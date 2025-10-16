import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    """Filter for Customer model with custom filters"""
    
    # Case-insensitive partial match for name
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name (contains)'
    )
    
    # Case-insensitive partial match for email
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='Email (contains)'
    )
    
    # Date range filters for created_at
    created_at_gte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Created after'
    )
    
    created_at_lte = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Created before'
    )
    
    # Custom filter: Match phone numbers starting with a pattern
    phone_starts_with = django_filters.CharFilter(
        field_name='phone',
        lookup_expr='startswith',
        label='Phone starts with (e.g., +1)'
    )
    
    # Bonus: Filter by exact phone
    phone = django_filters.CharFilter(
        field_name='phone',
        lookup_expr='icontains',
        label='Phone (contains)'
    )

    class Meta:
        model = Customer
        fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'created_at': ['gte', 'lte', 'exact'],
        }


class ProductFilter(django_filters.FilterSet):
    """Filter for Product model with price and stock ranges"""
    
    # Case-insensitive partial match for name
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name (contains)'
    )
    
    # Price range filters
    price_gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Price minimum'
    )
    
    price_lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Price maximum'
    )
    
    # Stock filters
    stock = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='exact',
        label='Stock (exact)'
    )
    
    stock_gte = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='gte',
        label='Stock minimum'
    )
    
    stock_lte = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='lte',
        label='Stock maximum'
    )
    
    # Custom filter: Low stock (less than specified amount)
    low_stock = django_filters.NumberFilter(
        field_name='stock',
        lookup_expr='lt',
        label='Low stock (less than)'
    )
    
    # Bonus: Out of stock
    out_of_stock = django_filters.BooleanFilter(
        method='filter_out_of_stock',
        label='Out of stock'
    )
    
    def filter_out_of_stock(self, queryset, name, value):
        """Custom method to filter out-of-stock products"""
        if value:
            return queryset.filter(stock=0)
        return queryset.exclude(stock=0)

    class Meta:
        model = Product
        fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte', 'lt'],
        }


class OrderFilter(django_filters.FilterSet):
    """Filter for Order model with customer and product relationships"""
    
    # Total amount range filters
    total_amount_gte = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='gte',
        label='Total amount minimum'
    )
    
    total_amount_lte = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='lte',
        label='Total amount maximum'
    )
    
    # Order date range filters
    order_date_gte = django_filters.DateTimeFilter(
        field_name='order_date',
        lookup_expr='gte',
        label='Order date after'
    )
    
    order_date_lte = django_filters.DateTimeFilter(
        field_name='order_date',
        lookup_expr='lte',
        label='Order date before'
    )
    
    # Filter by customer name (related field lookup)
    customer_name = django_filters.CharFilter(
        field_name='customer__name',
        lookup_expr='icontains',
        label='Customer name (contains)'
    )
    
    # Filter by customer email
    customer_email = django_filters.CharFilter(
        field_name='customer__email',
        lookup_expr='icontains',
        label='Customer email (contains)'
    )
    
    # Filter by customer ID
    customer_id = django_filters.NumberFilter(
        field_name='customer__id',
        lookup_expr='exact',
        label='Customer ID'
    )
    
    # Filter by product name (related field lookup)
    product_name = django_filters.CharFilter(
        field_name='products__name',
        lookup_expr='icontains',
        label='Product name (contains)',
        distinct=True  # Avoid duplicate results
    )
    
    # Filter by specific product ID
    product_id = django_filters.NumberFilter(
        field_name='products__id',
        lookup_expr='exact',
        label='Product ID',
        distinct=True  # Avoid duplicate results
    )
    
    # Bonus: Filter by multiple product IDs
    product_ids = django_filters.CharFilter(
        method='filter_product_ids',
        label='Product IDs (comma-separated)'
    )
    
    def filter_product_ids(self, queryset, name, value):
        """Custom method to filter by multiple product IDs"""
        if value:
            product_ids = [int(id.strip()) for id in value.split(',')]
            return queryset.filter(products__id__in=product_ids).distinct()
        return queryset

    class Meta:
        model = Order
        fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
        }