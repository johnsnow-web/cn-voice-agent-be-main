import os
import json
from decimal import Decimal
from django.core.management.base import BaseCommand
from inventory.models import User, Category, Product, Inventory
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Seed database with realistic data from seed_data_realistic.json'

    def handle(self, *args, **kwargs):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        json_path = os.path.join(BASE_DIR, 'seed_data_realistic.json')

        with open(json_path, 'r') as f:
            data = json.load(f)

        self.stdout.write("🚮 Clearing old data...")
        Inventory.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("👤 Inserting users...")
        for item in data['user']:
            User.objects.create(
                id=item['id'],
                name=item['name'],
                email=item['email'],
                password=make_password(item['password']),
                add1=item['add1'],
                add2=item.get('add2'),
                area=item['area'],
                city=item['city'],
                pincode=item['pincode'],
                state=item['state'],
                countryCode=item['countryCode']
            )

        self.stdout.write("📂 Inserting categories...")
        for item in data['category']:
            Category.objects.create(
                id=item['id'],
                name=item['name']
            )

        self.stdout.write("📦 Inserting products...")
        for item in data['product']:
            user_instance = User.objects.get(id=item['user_id'])
            category_instance = Category.objects.get(id=item['category_id'])
            Product.objects.create(
                id=item['id'],
                user=user_instance,
                category=category_instance,
                name=item['name'],
                price=Decimal(item['price']),
                description=item['description'],
                unit=item['unit'],
                deleted=item['deleted'],
                image=item['image']
            )

        self.stdout.write("📊 Inserting inventory...")
        for item in data['inventory']:
            product_instance = Product.objects.get(id=item['product_id'])
            Inventory.objects.create(
                product=product_instance,
                quantity=item['quantity'],
                reorderLevel=5
            )

        self.stdout.write(self.style.SUCCESS("✅ Database successfully seeded with realistic data."))