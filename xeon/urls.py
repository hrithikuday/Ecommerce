from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router Setup
router = DefaultRouter()
router.register('categories', views.CategoryViewSet, basename='api-category')
router.register('products', views.ProductViewSet, basename='api-product')
router.register('cart', views.CartViewSet, basename='api-cart')
router.register('orders', views.OrderViewSet, basename='api-order')
router.register('media-urls', views.MediaURLViewSet, basename='api-media-url')

urlpatterns = [
    # Standard Web Pages
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('account/delete/', views.delete_account, name='delete_account'),

    # REST API Routes
    path('api/', include(router.urls)),
    path('api/auth/login/', views.AuthAPIView.as_view(), name='api-login'),
]
