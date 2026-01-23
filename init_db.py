import asyncio
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import engine, AsyncSessionLocal, Base
from app.core.security import get_password_hash
from app.models.user import User
from app.models.product import Product
from app.models.shop import Shop
from app.models.membership import Membership
from app.models.cart import Cart


async def create_tables() -> None:
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created successfully")


async def seed_data() -> None:
    """Seed database with sample data."""
    print("\nSeeding database with sample data...")

    async with AsyncSessionLocal() as db:
        try:
            # Create membership tiers
            memberships = [
                Membership(tier="bronze", discount_percentage=5, annual_fee=0),
                Membership(tier="silver", discount_percentage=10, annual_fee=49.99),
                Membership(tier="gold", discount_percentage=15, annual_fee=99.99),
            ]
            for m in memberships:
                db.add(m)
            await db.commit()
            print("✓ Membership tiers created")

            # Create sample users
            users_data = [
                {
                    "username": "alice_smith",
                    "email": "alice@techhouse.com",
                    "full_name": "Alice Smith",
                    "password": "AliceSecure123!",
                },
                {
                    "username": "bob_jones",
                    "email": "bob@techhouse.com",
                    "full_name": "Bob Jones",
                    "password": "BobSecure123!",
                },
                {
                    "username": "carol_white",
                    "email": "carol@techhouse.com",
                    "full_name": "Carol White",
                    "password": "CarolSecure123!",
                },
            ]

            users = []
            for user_data in users_data:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    is_active=True,
                    membership_type="bronze",
                )
                db.add(user)
                users.append(user)

            await db.commit()
            # Refresh to get IDs
            for user in users:
                await db.refresh(user)
            print(f"✓ {len(users)} sample users created")

            # Create carts for users
            for user in users:
                cart = Cart(user_id=user.id, status="active")
                db.add(cart)
            await db.commit()
            print(f"✓ {len(users)} shopping carts created")

            # Create sample shops
            shops_data = [
                {
                    "name": "Apple Store Official",
                    "description": "Official Apple products and accessories",
                    "owner_id": users[0].id,
                },
                {
                    "name": "Samsung Hub",
                    "description": "Latest Samsung phones, tablets, and electronics",
                    "owner_id": users[1].id,
                },
                {
                    "name": "Tech Accessories Pro",
                    "description": "Premium accessories for all devices",
                    "owner_id": users[2].id,
                },
            ]

            shops = []
            for shop_data in shops_data:
                shop = Shop(
                    name=shop_data["name"],
                    description=shop_data["description"],
                    owner_id=shop_data["owner_id"],
                    is_active=True,
                )
                db.add(shop)
                shops.append(shop)

            await db.commit()
            for shop in shops:
                await db.refresh(shop)
            print(f"✓ {len(shops)} sample shops created")

            # Create sample products
            products_data = [
                # Apple products
                {
                    "name": "iPhone 15 Pro Max",
                    "description": "Latest flagship smartphone with advanced camera",
                    "price": 1199.99,
                    "stock": 25,
                    "category": "Smartphones",
                    "sku": "APPLE-IP15PM-001",
                    "shop_id": shops[0].id,
                },
                {
                    "name": "MacBook Pro 16",
                    "description": "Powerful laptop for professionals",
                    "price": 2499.99,
                    "stock": 10,
                    "category": "Laptops",
                    "sku": "APPLE-MBP16-001",
                    "shop_id": shops[0].id,
                },
                # Samsung products
                {
                    "name": "Samsung Galaxy S24",
                    "description": "Premium Android smartphone with AI features",
                    "price": 999.99,
                    "stock": 30,
                    "category": "Smartphones",
                    "sku": "SAMSUNG-S24-001",
                    "shop_id": shops[1].id,
                },
                {
                    "name": "Samsung 4K Smart TV",
                    "description": "65-inch 4K display with smart features",
                    "price": 799.99,
                    "stock": 5,
                    "category": "Home Appliances",
                    "sku": "SAMSUNG-TV65-001",
                    "shop_id": shops[1].id,
                },
                # Accessories
                {
                    "name": "USB-C Charging Cable",
                    "description": "Fast charging cable, 2-meter length",
                    "price": 19.99,
                    "stock": 100,
                    "category": "Accessories",
                    "sku": "ACC-USBC-001",
                    "shop_id": shops[2].id,
                },
                {
                    "name": "Wireless Earbuds Pro",
                    "description": "Premium noise-cancelling earbuds",
                    "price": 299.99,
                    "stock": 45,
                    "category": "Audio",
                    "sku": "ACC-BUDS-001",
                    "shop_id": shops[2].id,
                },
            ]

            for product_data in products_data:
                product = Product(**product_data)
                db.add(product)

            await db.commit()
            print(f"✓ {len(products_data)} sample products created")

            print("\n✅ Database seeding completed successfully!")
            print("\nSample Credentials:")
            print("  Username: alice_smith | Password: AliceSecure123!")
            print("  Username: bob_jones   | Password: BobSecure123!")
            print("  Username: carol_white | Password: CarolSecure123!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


async def async_main() -> None:
    """Async main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize TechHouse database")
    parser.add_argument(
        "--seed", action="store_true", help="Seed database with sample data"
    )

    args = parser.parse_args()

    try:
        await create_tables()

        if args.seed:
            await seed_data()
        else:
            print("\n💡 Tip: Run with --seed flag to add sample data")
            print("   python init_db.py --seed")

        print("\n✨ Database initialization complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(async_main())
