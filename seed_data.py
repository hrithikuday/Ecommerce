import os
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from xeon.models import User, Category, Product, Cart, CartItem, Order, OrderItem, Payment, MediaURL

def seed():
    print("Starting database seeding...")

    # Clear old database records to avoid conflicts
    print("Cleaning database...")
    Payment.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    CartItem.objects.all().delete()
    Cart.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    MediaURL.objects.all().delete()

    # 1. Create Users
    print("Creating user profiles...")
    seller, created = User.objects.get_or_create(
        username='xeonadmin',
        defaults={
            'email': 'admin@xeon.com',
            'role': User.SELLER,
            'is_staff': True,
            'is_superuser': True,
            'phone': '+1 (555) 902-1337',
            'address': 'Xeon Headquarters, Suite 100, San Francisco, CA'
        }
    )
    if created:
        seller.set_password('password123')
        seller.save()
        print("-> Created Seller/Admin User: xeonadmin / password123")
    else:
        # In case the user exists but password needs resetting
        seller.set_password('password123')
        seller.role = User.SELLER
        seller.is_staff = True
        seller.is_superuser = True
        seller.save()
        print("-> Seller/Admin user updated")

    buyer, created = User.objects.get_or_create(
        username='xeonbuyer',
        defaults={
            'email': 'buyer@xeon.com',
            'role': User.BUYER,
            'phone': '+1 (555) 123-4567',
            'address': '789 Minimalist Blvd, Los Angeles, CA'
        }
    )
    if created:
        buyer.set_password('password123')
        buyer.save()
        print("-> Created Buyer User: xeonbuyer / password123")
    else:
        buyer.set_password('password123')
        buyer.role = User.BUYER
        buyer.save()
        print("-> Buyer user updated")

    # 2. Create Categories
    print("Creating product categories...")
    categories_data = [
        {
            'name': 'Mobiles',
            'description': 'High-performance smartphones and mobile accessories.',
            'image_url': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=80'
        },
        {
            'name': 'Fashion',
            'description': 'Premium outerwear, designer footwear, and structural apparel.',
            'image_url': 'https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&auto=format&fit=crop&q=80'
        },
        {
            'name': 'Books',
            'description': 'Handpicked literature spanning technology, design, and philosophy.',
            'image_url': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=800&auto=format&fit=crop&q=80'
        },
        {
            'name': 'Appliances',
            'description': 'Bespoke precision appliances designed for seamless living.',
            'image_url': 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=800&auto=format&fit=crop&q=80'
        },
        {
            'name': 'Beauty',
            'description': 'Luxury skincare formulas and sophisticated fragrances.',
            'image_url': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&auto=format&fit=crop&q=80'
        }
    ]

    categories = {}
    for c_data in categories_data:
        cat, cat_created = Category.objects.get_or_create(
            name=c_data['name'],
            defaults={
                'description': c_data['description'],
                'image_url': c_data['image_url']
            }
        )
        categories[c_data['name']] = cat
        if cat_created:
            print(f"-> Created Category: {c_data['name']}")

    # 3. Create Products
    print("Creating demo products...")
    products_data = [
        # Mobiles
        {
            'category': 'Mobiles',
            'name': 'iPhone 15 Pro Max',
            'price': Decimal('1199.00'),
            'stock': 50,
            'description': 'Aerospace-grade titanium design, featuring the ground-breaking A17 Pro chip, customizable Action button, and the most powerful iPhone camera system ever.',
            'image_url': 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Mobiles',
            'name': 'Samsung Galaxy S24 Ultra',
            'price': Decimal('1299.00'),
            'stock': 40,
            'description': 'Welcome to the era of mobile AI. With Galaxy S24 Ultra in your hands, you can unleash whole new levels of creativity, productivity and possibility.',
            'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Mobiles',
            'name': 'OnePlus 12 Black Edition',
            'price': Decimal('799.00'),
            'stock': 35,
            'description': 'Redefined flagship smartphone featuring Snapdragon 8 Gen 3, 4th Gen Hasselblad Camera for Mobile, and super-fast 100W SUPERVOOC charging.',
            'image_url': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&auto=format&fit=crop&q=80'
        },
        
        # Fashion
        {
            'category': 'Fashion',
            'name': 'Designer Leather Jacket',
            'price': Decimal('199.99'),
            'stock': 15,
            'description': 'Premium lambskin leather jacket with sleek silver asymmetrical hardware and a tailored fit for timeless structural luxury.',
            'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Fashion',
            'name': 'Minimalist Obsidian Sneakers',
            'price': Decimal('120.00'),
            'stock': 25,
            'description': 'All-black designer sneakers crafted with premium breathable mesh and custom memory-foam cushions for structured comfort.',
            'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Fashion',
            'name': 'Structured Wool Trench Coat',
            'price': Decimal('250.00'),
            'stock': 10,
            'description': 'Double-breasted trench coat built from premium heavy wool blend, featuring detailed structured collars and hidden security compartments.',
            'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=800&auto=format&fit=crop&q=80'
        },
        
        # Books
        {
            'category': 'Books',
            'name': 'Clean Code by Robert C. Martin',
            'price': Decimal('35.00'),
            'stock': 100,
            'description': 'A handbook of agile software craftsmanship. Master the principles, patterns, and practices of writing clean, high-performance code.',
            'image_url': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Books',
            'name': 'The Design of Everyday Things',
            'price': Decimal('25.00'),
            'stock': 80,
            'description': 'Even the smartest among us can feel inept as we fail to figure out which light switch or oven burner to turn on. Cognitive science meets elegant industrial design.',
            'image_url': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Books',
            'name': 'Zero to One by Peter Thiel',
            'price': Decimal('20.00'),
            'stock': 60,
            'description': 'Notes on startups, or how to build the future. Learn the philosophy of going from zero to one and creating singular value in the marketplace.',
            'image_url': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=800&auto=format&fit=crop&q=80'
        },

        # Appliances
        {
            'category': 'Appliances',
            'name': 'Precision Espresso Machine',
            'price': Decimal('499.00'),
            'stock': 8,
            'description': 'Bespoke dual-boiler espresso maker with built-in PID digital temperature control, premium steam wand, and high-pressure extraction capabilities.',
            'image_url': 'https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Appliances',
            'name': 'Air Purifier Pro',
            'price': Decimal('180.00'),
            'stock': 20,
            'description': 'High-efficiency True HEPA filter air purifier with real-time smart sensing, silent night mode, and elegant structural cylindrical build.',
            'image_url': 'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Appliances',
            'name': 'Minimalist Glass Toaster',
            'price': Decimal('60.00'),
            'stock': 15,
            'description': 'Two-slice toaster with custom see-through glass panels and highly precise touch screen control for flawless browning adjustments.',
            'image_url': 'https://images.unsplash.com/photo-1583228966902-613d9646c071?w=800&auto=format&fit=crop&q=80'
        },

        # Beauty
        {
            'category': 'Beauty',
            'name': 'Hydrating Face Serum',
            'price': Decimal('45.00'),
            'stock': 150,
            'description': 'Advanced formula featuring double hyaluronic acid and pure vitamin C to lock in deep skin moisture and restore radiant, structural glow.',
            'image_url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Beauty',
            'name': 'Luxury Fragrance (Obsidian)',
            'price': Decimal('95.00'),
            'stock': 30,
            'description': 'A highly sophisticated, gender-neutral parfum combining notes of smoky sandalwood, rich amber, and crushed cardamon for an enigmatic trail.',
            'image_url': 'https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&auto=format&fit=crop&q=80'
        },
        {
            'category': 'Beauty',
            'name': 'Velvet Matte Crimson Lipstick',
            'price': Decimal('28.00'),
            'stock': 65,
            'description': 'Long-lasting lipstick with a rich velvet matte finish, lightweight moisture formula, and highly intense pigments in classic deep crimson.',
            'image_url': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800&auto=format&fit=crop&q=80'
        }
    ]

    products = []
    for p_data in products_data:
        prod, prod_created = Product.objects.get_or_create(
            name=p_data['name'],
            defaults={
                'category': categories[p_data['category']],
                'price': p_data['price'],
                'currency': p_data.get('currency', '$'),
                'stock': p_data['stock'],
                'description': p_data['description'],
                'image_url': p_data['image_url'],
                'is_active': True
            }
        )
        products.append(prod)
        if prod_created:
            print(f"-> Created Product: {p_data['name']} under {p_data['category']}")

    # 4. Create Fake Orders
    print("Creating historical fake orders...")
    statuses = [Order.PAID, Order.SHIPPED, Order.DELIVERED]
    methods = ['Credit Card', 'PayPal', 'UPI / NetBanking']

    # Generate 5 fake orders for the buyer
    import uuid
    for i in range(1, 6):
        # Pick 1-3 random products
        selected_prods = random.sample(products, random.randint(1, 3))
        total_amount = Decimal('0.00')
        
        # Calculate amount
        order_items_cache = []
        for p in selected_prods:
            qty = random.randint(1, 2)
            item_price = p.price
            total_amount += item_price * qty
            order_items_cache.append((p, qty, item_price))

        # Date offsets to make them historical
        order_date = datetime.now() - timedelta(days=random.randint(2, 20))
        
        # Create Order
        order = Order.objects.create(
            user=buyer,
            total_amount=total_amount,
            status=random.choice(statuses),
            shipping_address="789 Minimalist Blvd, Los Angeles, CA",
            billing_address="789 Minimalist Blvd, Los Angeles, CA",
        )
        # Hack the auto_now_add creation date for historical statistics
        Order.objects.filter(id=order.id).update(created_at=order_date)

        # Create Items
        for p, qty, price in order_items_cache:
            OrderItem.objects.create(
                order=order,
                product=p,
                price=price,
                currency=p.currency,
                quantity=qty
            )
            # Adjust product stock slightly
            p.stock = max(0, p.stock - qty)
            p.save()

        # Create Payment
        Payment.objects.create(
            order=order,
            payment_method=random.choice(methods),
            transaction_id=str(uuid.uuid4()).replace('-', '').upper()[:16],
            amount=order.total_amount,
            status=Payment.COMPLETED,
            created_at=order_date
        )
        print(f"-> Seeded Order #{order.id} with amount ${order.total_amount}")

    # 5. Create default MediaURL
    print("Creating default MediaURL links...")
    MediaURL.objects.get_or_create(
        title="Xeon Brand Guidelines & Assets",
        defaults={
            'user': seller,
            'url': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800',
            'url_type': MediaURL.IMAGE
        }
    )
    MediaURL.objects.get_or_create(
        title="Tactile Floating Desk Craft Video",
        defaults={
            'user': seller,
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'url_type': MediaURL.VIDEO
        }
    )
    print("-> Seeded default media URLs")

    print("\nDatabase seeding completed successfully!")

if __name__ == '__main__':
    seed()
