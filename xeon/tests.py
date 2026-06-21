from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment, MediaURL

# =====================================================================
# DJANGO STANDARD UNIT TESTS
# =====================================================================

class XeonModelTestCase(TestCase):
    def setUp(self):
        # Create standard test roles
        self.buyer_user = User.objects.create_user(
            username='buyer', email='buyer@xeon.com', password='password123', role=User.BUYER
        )
        self.seller_user = User.objects.create_user(
            username='seller', email='seller@xeon.com', password='password123', role=User.SELLER
        )
        
        # Create test category and products
        self.category = Category.objects.create(name="Electronics", description="High-end sound systems")
        self.product = Product.objects.create(
            category=self.category,
            name="Xeon Soundbar V1",
            price=299.99,
            stock=15,
            description="Pure acoustic fidelity."
        )

    def test_user_roles(self):
        self.assertFalse(self.buyer_user.is_seller())
        self.assertTrue(self.seller_user.is_seller())
        self.assertEqual(str(self.buyer_user), "buyer (BUYER)")

    def test_product_slug_auto_generation(self):
        self.assertEqual(self.product.slug, "xeon-soundbar-v1")
        self.assertEqual(self.category.slug, "electronics")

    def test_cdn_image_url_resolver(self):
        # Verify fallback image
        self.assertTrue(self.product.get_image_url.startswith("https://"))
        self.assertTrue(self.category.get_image_url.startswith("https://"))


class XeonViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.buyer = User.objects.create_user(
            username='buyer', email='buyer@xeon.com', password='password123', role=User.BUYER
        )
        self.seller = User.objects.create_user(
            username='seller', email='seller@xeon.com', password='password123', role=User.SELLER
        )
        
        self.category = Category.objects.create(name="Audio")
        self.product = Product.objects.create(
            category=self.category, name="Xeon Buds", price=120.00, stock=10, description="Sound."
        )

    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buds")

    def test_product_detail_page_status(self):
        response = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buds")

    def test_buyer_dashboard_orders_listing(self):
        self.client.login(username='buyer', password='password123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ORDER HISTORY")


    def test_cart_workflow(self):
        self.client.login(username='buyer', password='password123')
        
        # Add to cart
        response = self.client.get(reverse('add_to_cart', kwargs={'product_id': self.product.id}))
        self.assertEqual(response.status_code, 302)  # Redirects to cart
        
        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.get_item_count, 1)
        self.assertEqual(cart.get_total_price, 120.00)

        # Checkout
        response = self.client.post(reverse('checkout'), {
            'shipping_address': '123 Test St, Tech City',
            'payment_method': 'Credit Card'
        })
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard
        
        # Verify order was generated
        orders = Order.objects.filter(user=self.buyer)
        self.assertEqual(orders.count(), 1)
        order = orders.first()
        self.assertEqual(order.total_amount, 120.00)
        self.assertEqual(order.status, Order.PAID)
        
        # Verify product stock reduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

    def test_account_deletion(self):
        self.client.login(username='buyer', password='password123')
        response = self.client.post(reverse('delete_account'))
        self.assertEqual(response.status_code, 302)
        user_exists = User.objects.filter(username='buyer').exists()
        self.assertFalse(user_exists)

    def test_custom_404_page(self):
        response = self.client.get('/invalid-url-path-that-does-not-exist/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "PAGE NOT FOUND", status_code=404)


# =====================================================================
# DJANGO REST FRAMEWORK (DRF) API TESTS
# =====================================================================

class XeonAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='apitest', email='apitest@xeon.com', password='password123'
        )
        self.category = Category.objects.create(name="Wearables")
        self.product = Product.objects.create(
            category=self.category, name="Xeon Watch", price=450.00, stock=5, description="Watch."
        )
        
        # Obtain auth token
        response = self.client.post(reverse('api-login'), {
            'username': 'apitest',
            'password': 'password123'
        })
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_api_products_list(self):
        response = self.client.get(reverse('api-product-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Xeon Watch")

    def test_api_cart_management(self):
        # Fetch empty cart
        response = self.client.get(reverse('api-cart-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Add product via API
        response = self.client.post(reverse('api-cart-add-item'), {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item_count'], 2)

    def test_api_media_urls_custom_add(self):
        # Add custom resource link via API
        response = self.client.post(reverse('api-media-url-list'), {
            'title': 'Campaign Ad Video',
            'url': 'https://youtube.com/watch?v=xeonad1',
            'url_type': 'VIDEO'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        media_count = MediaURL.objects.filter(user=self.user).count()
        self.assertEqual(media_count, 1)

    def test_api_create_product(self):
        # POST to /api/products/
        response = self.client.post(reverse('api-product-list'), {
            'category': self.category.id,
            'name': 'Xeon Buds X',
            'price': '199.99',
            'stock': 20,
            'description': 'Premium noise canceling buds.',
            'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name='Xeon Buds X').exists())

    def test_api_update_product(self):
        # PUT to /api/products/<slug>/
        response = self.client.put(reverse('api-product-detail', kwargs={'slug': self.product.slug}), {
            'category': self.category.id,
            'name': 'Xeon Watch Gen 2',
            'price': '499.99',
            'stock': 10,
            'description': 'Updated model.'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Xeon Watch Gen 2')
        self.assertEqual(self.product.price, Decimal('499.99'))

    def test_api_delete_product(self):
        # DELETE to /api/products/<slug>/
        response = self.client.delete(reverse('api-product-detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_api_create_category(self):
        # POST to /api/categories/
        response = self.client.post(reverse('api-category-list'), {
            'name': 'Tablets',
            'description': 'High-resolution sleek tablets.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name='Tablets').exists())

    def test_api_delete_category(self):
        # DELETE to /api/categories/<slug>/
        response = self.client.delete(reverse('api-category-detail', kwargs={'slug': self.category.slug}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())
