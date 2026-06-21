from rest_framework import serializers
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment, MediaURL

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'address']
        read_only_fields = ['id', 'role']


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image_url', 'get_image_url', 'product_count']
        read_only_fields = ['id', 'slug', 'get_image_url', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 'description', 
            'price', 'currency', 'stock', 'image_url', 'get_image_url', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'category_name', 'get_image_url', 'created_at']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True), 
        write_only=True, 
        source='product'
    )
    total_price = serializers.DecimalField(source='get_total_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(source='get_total_price', max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(source='get_item_count', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'item_count']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.DecimalField(source='get_total_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'currency', 'quantity', 'total_price']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_method', 'transaction_id', 'amount', 'status', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'status', 'shipping_address', 'billing_address', 'items', 'payment', 'created_at']
        read_only_fields = ['id', 'user', 'total_amount', 'status', 'payment', 'created_at']


class MediaURLSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MediaURL
        fields = ['id', 'username', 'title', 'url', 'url_type', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_url(self, value):
        if not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError("URL must start with http:// or https://")
        return value
