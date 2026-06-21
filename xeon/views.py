from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse

# DRF Imports
from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

# Models, Serializers, Forms
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment, MediaURL
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer, CartSerializer, 
    CartItemSerializer, OrderSerializer, MediaURLSerializer
)
from .forms import LoginForm, RegisterForm, MediaURLForm

# =====================================================================
# TEMPLATE-BASED HTML VIEWS
# =====================================================================

def home(request):
    """
    Landing page showcasing categories and products.
    Optimized with select_related for products query.
    """
    categories = Category.objects.annotate(product_count=Count('products')).all()
    
    # Query parameters
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    
    products = Product.objects.select_related('category').filter(is_active=True)
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    # Get active cart count
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_item_count

    context = {
        'categories': categories,
        'products': products,
        'selected_category': category_slug,
        'search_query': search_query,
        'cart_count': cart_count,
    }
    return render(request, 'xeon/home.html', context)


def product_detail(request, slug):
    """
    Detailed product page.
    """
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    
    cart_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.get_item_count

    context = {
        'product': product,
        'related_products': related_products,
        'cart_count': cart_count,
    }
    return render(request, 'xeon/product_detail.html', context)


@login_required
def cart_view(request):
    """
    Cart management page.
    Optimized with prefetch_related on items and products.
    """
    cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        
        if action == 'remove' and item_id:
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        elif action == 'update' and item_id:
            quantity = int(request.POST.get('quantity', 1))
            cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
            if quantity > 0:
                if quantity <= cart_item.product.stock:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, "Cart updated.")
                else:
                    messages.error(request, f"Sorry, only {cart_item.product.stock} items in stock.")
            else:
                cart_item.delete()
                messages.success(request, "Item removed from cart.")
                
        return redirect('cart')

    return render(request, 'xeon/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    """
    Add product to cart (redirects back to cart).
    """
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {product.name} to cart.")
        else:
            messages.error(request, f"Cannot add more. Only {product.stock} in stock.")
    else:
        if product.stock > 0:
            cart_item.quantity = 1
            cart_item.save()
            messages.success(request, f"{product.name} added to cart.")
        else:
            cart_item.delete()
            messages.error(request, "This product is currently out of stock.")
            
    return redirect('cart')


@login_required
def checkout_view(request):
    """
    Checkout processing page.
    """
    cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=request.user)
    if cart.get_item_count == 0:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address', shipping_address)
        payment_method = request.POST.get('payment_method', 'Credit Card')

        if not shipping_address:
            messages.error(request, "Please enter a shipping address.")
            return redirect('checkout')

        # Create Order
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.get_total_price,
            shipping_address=shipping_address,
            billing_address=billing_address,
            status=Order.PAID  # Simulating immediate payment success for this flow
        )

        # Create Order Items and adjust stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            # Reduce product stock
            product = item.product
            product.stock = max(0, product.stock - item.quantity)
            product.save()

        # Create Mock Payment
        import uuid
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            transaction_id=str(uuid.uuid4()).replace('-', '').upper()[:16],
            amount=order.total_amount,
            status=Payment.COMPLETED
        )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f"Order #{order.id} placed successfully! Thank you for shopping with Xeon.")
        return redirect('dashboard')

    return render(request, 'xeon/checkout.html', {'cart': cart})


def signup_view(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Xeon, {user.username}!")
            return redirect('home')
    else:
        form = RegisterForm()
        
    return render(request, 'xeon/register.html', {'form': form})


def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
        
    return render(request, 'xeon/login.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_view(request):
    """
    Client/Buyer Dashboard featuring purchase history and profile information.
    """
    orders = Order.objects.prefetch_related('items__product').filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'is_seller_view': False
    }
    return render(request, 'xeon/dashboard.html', context)


@login_required
def delete_account(request):
    """
    Allows customers to delete their profile credentials.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')
    return redirect('dashboard')




# =====================================================================
# DJANGO REST FRAMEWORK (DRF) API VIEWS
# =====================================================================

class AuthAPIView(APIView):
    """
    Custom endpoint for Token based authentication
    """
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing, creating, updating, and deleting categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing, creating, updating, and deleting products.
    Optimized queries with select_related category.
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        # Allow viewing inactive products during writes/edits if needed, or filter by is_active for standard GET requests
        if self.action in ['list', 'retrieve']:
            queryset = Product.objects.select_related('category').filter(is_active=True)
        else:
            queryset = Product.objects.select_related('category')
            
        category_slug = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return queryset


class CartViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing the shopping cart.
    Requires Authentication.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=self.request.user)
        return cart

    def list(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        """
        Custom POST API endpoint to add an item to user's cart.
        """
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock < quantity:
            return Response({'error': f'Only {product.stock} items available in stock.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cart_item.quantity + quantity <= product.stock:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                return Response({'error': f'Cannot add. Stock limit reached. Max stock: {product.stock}.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            cart_item.quantity = quantity
            cart_item.save()

        cart = self.get_object()
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=['post'], url_path='update')
    def update_item(self, request):
        """
        Custom POST API endpoint to update item quantity in cart.
        """
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity <= 0:
            cart_item.delete()
            cart = self.get_object()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        if cart_item.product.stock < quantity:
            return Response({'error': f'Only {cart_item.product.stock} items in stock.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()
        cart = self.get_object()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @decorators.action(detail=False, methods=['post'], url_path='clear')
    def clear_cart(self, request):
        """
        Custom action to empty the cart.
        """
        cart = self.get_object()
        cart.items.all().delete()
        cart = self.get_object()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for placing and retrieving orders.
    Requires Authentication.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        return Order.objects.prefetch_related('items__product').filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        if cart.get_item_count == 0:
            raise serializers.ValidationError("Your shopping cart is empty.")

        # Save order details
        order = serializer.save(
            user=self.request.user,
            total_amount=cart.get_total_price,
            status=Order.PAID
        )

        # Create OrderItems and reduce stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )
            # Reduce inventory
            product = item.product
            product.stock = max(0, product.stock - item.quantity)
            product.save()

        # Mock transaction and create Payment log
        import uuid
        Payment.objects.create(
            order=order,
            payment_method="API Checkout",
            transaction_id=str(uuid.uuid4()).replace('-', '').upper()[:16],
            amount=order.total_amount,
            status=Payment.COMPLETED
        )

        # Empty cart
        cart.items.all().delete()


class MediaURLViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing custom links and media URLs dynamically.
    Authenticated users can perform full CRUD on their links.
    """
    serializer_class = MediaURLSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    def get_queryset(self):
        # Admin or Sellers can view all media links, buyers view their own
        if self.request.user.is_seller():
            return MediaURL.objects.all().order_by('-created_at')
        return MediaURL.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def custom_404_view(request, exception=None):
    """
    Custom premium dark-themed 404 error page.
    """
    return render(request, 'xeon/404.html', status=404)
