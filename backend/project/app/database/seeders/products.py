from faker import Faker
from sqlalchemy.orm import Session
from tqdm.asyncio import tqdm
from ..tables import Product, Category, Supplier
from PIL import Image, ImageDraw
import os
import random

fake = Faker()

def generate_gradient_image(file_path: str, width: int = 200, height: int = 200):
    img = Image.new("RGB", (width, height), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    start_color = tuple(random.randint(0, 255) for _ in range(3))
    end_color = tuple(random.randint(0, 255) for _ in range(3))

    for i in range(width):
        ratio = i / width
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.line([(i, 0), (i, height)], fill=(r, g, b))

    img.save(file_path)
    

async def seed_products(db: Session, num_products: int, batch_size: int = 1000):
    categories = db.query(Category).all()
    suppliers = db.query(Supplier).all()

    category_ids = [c.id for c in categories]
    supplier_ids = [s.id for s in suppliers]
    products_to_add = []
    
    name_count = {}

    async for _ in tqdm(range(num_products), desc="Seeding Products"):
        base_name = fake.word()

        if base_name in name_count:
            name_count[base_name] += 1
            product_name = f"{base_name}{name_count[base_name]}"
        else:
            name_count[base_name] = 1
            product_name = base_name

        photo_path = f"static/images/{product_name}.png"
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        generate_gradient_image(photo_path)

        product = Product(
            name=product_name,
            description=fake.text(max_nb_chars=200),
            price=fake.random_number(digits=3),
            category_id=fake.random_element(elements=category_ids),
            supplier_id=fake.random_element(elements=supplier_ids),
            quantity=fake.random_number(digits=2),
            photo_path=photo_path,
        )
        products_to_add.append(product)

        if len(products_to_add) >= batch_size:
            db.bulk_save_objects(products_to_add)
            db.commit()
            products_to_add = []

    if products_to_add:
        db.bulk_save_objects(products_to_add)
        db.commit()
