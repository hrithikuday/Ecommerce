from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment, MediaURL

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'address')}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products Count'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'currency', 'stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('-created_at',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'get_item_count', 'get_total_price')
    inlines = [CartItemInline]
    search_fields = ('user__username', 'id')

    def get_item_count(self, obj):
        return obj.get_item_count
    get_item_count.short_description = 'Total Items'

    def get_total_price(self, obj):
        return obj.get_total_price
    get_total_price.short_description = 'Total Price'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'id')
    ordering = ('-created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'amount', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('order__id', 'transaction_id')


@admin.register(MediaURL)
class MediaURLAdmin(admin.ModelAdmin):
    list_display = ('title', 'url_type', 'user', 'created_at')
    list_filter = ('url_type', 'created_at')
    search_fields = ('title', 'url', 'user__username')
