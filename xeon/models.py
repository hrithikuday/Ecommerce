from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify

class User(AbstractUser):
    BUYER = 'BUYER'
    SELLER = 'SELLER'
    
    ROLE_CHOICES = [
        (BUYER, 'Buyer'),
        (SELLER, 'Seller / Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=BUYER)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def is_seller(self):
        return self.role == self.SELLER or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            cdn = getattr(settings, 'CDN_URL', '')
            return f"{cdn}{settings.MEDIA_URL}{self.image.name}"
        return "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&auto=format&fit=crop&q=80"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price
    currency = models.CharField(
        max_length=10,
        choices=[
            ('$', 'USD ($)'),
            ('₹', 'INR (₹)'),
            ('€', 'EUR (€)'),
            ('£', 'GBP (£)'),
            ('¥', 'JPY (¥)'),
            ('A$', 'AUD (A$)'),
            ('C$', 'CAD (C$)'),
            ('AED', 'AED'),
            ('SAR', 'SAR'),
        ],
        default='$'
    )
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            cdn = getattr(settings, 'CDN_URL', '')
            return f"{cdn}{settings.MEDIA_URL}{self.image.name}"
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80"

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'Guest'}"

    @property
    def get_total_price(self):
        return sum(item.get_total_price for item in self.items.all())

    @property
    def get_total_price_display(self):
        first_item = self.items.first()
        symbol = first_item.product.currency if (first_item and first_item.product) else '$'
        return f"{symbol}{self.get_total_price:.2f}"

    @property
    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def get_total_price(self):
        return self.product.price * self.quantity

    @property
    def get_price_display(self):
        return f"{self.product.currency}{self.product.price}"

    @property
    def get_total_price_display(self):
        return f"{self.product.currency}{self.get_total_price:.2f}"


class Order(models.Model):
    PENDING = 'PENDING'
    PAID = 'PAID'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
    CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    @property
    def get_total_price_display(self):
        first_item = self.items.first()
        symbol = first_item.currency if first_item else '$'
        return f"{symbol}{self.total_amount:.2f}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at purchase
    currency = models.CharField(max_length=10, default='$')
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'}"

    @property
    def get_total_price(self):
        return self.price * self.quantity

    @property
    def get_price_display(self):
        return f"{self.currency}{self.price}"

    @property
    def get_total_price_display(self):
        return f"{self.currency}{self.get_total_price:.2f}"


class Payment(models.Model):
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, default='Credit Card')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount} for Order #{self.order.id} - Status: {self.status}"


class MediaURL(models.Model):
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'
    DOCUMENT = 'DOCUMENT'
    OTHER = 'OTHER'

    TYPE_CHOICES = [
        (IMAGE, 'Image URL'),
        (VIDEO, 'Video URL'),
        (DOCUMENT, 'Document URL'),
        (OTHER, 'Other Link'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_urls')
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=1000)
    url_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default=OTHER)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.url_type})"
