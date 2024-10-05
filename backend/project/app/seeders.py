import asyncio
import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import Depends
from database.database import get_db
from database.seeders.categories import seed_categories
from database.seeders.suppliers import seed_suppliers
from database.seeders.products import seed_products
from database.seeders.orders import seed_orders
from database.tables import (
    Category,
    Supplier,
    Product,
    Order,
    User,
)
from database.database import SessionLocal
from database.database import engine, Base
from schemas.schemas import UserCreate
from controllers.auth_controller import register_new_user


def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


def create_main_user():
    user = UserCreate(username="root", email="root@root.root", password="root")
    db = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    
    if existing_user is None:
        register_new_user(user, db)
        print("Main user created.")
    else:
        print("Main user already exists.")

    db.close()


async def clear_db(db: Session):
    db.execute(text("DELETE FROM order_product"))
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(Supplier).delete()
    db.commit()
    print("Database cleared")


async def seed():
    start_time = time.time()
    db = SessionLocal()
    try:
        await clear_db(db)
        await seed_suppliers(db, 50)
        await seed_categories(db, 10)
        await seed_products(db, 1000)
        await seed_orders(db, 50)
    finally:
        db.close()

    elapsed_time = time.time() - start_time
    print(f"Seeding completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    create_tables()
    #create_main_user()
    asyncio.run(seed())
