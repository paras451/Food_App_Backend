# FOODAPPLICATION/management/commands/seed_foods.py
from django.core.management.base import BaseCommand
from FOODAPPLICATION.models import Food

class Command(BaseCommand):
    help = "Seed food items into database"

    def handle(self, *args, **kwargs):
        foods= [
    {"id": 1, "name": "Butter Chicken",  "state": "Punjab",        "price": 299, "description": "Creamy tomato-based chicken curry", "image": "food_images/butter-chicken.jpg"},
    {"id": 2, "name": "Dal Baati",        "state": "Rajasthan",     "price": 249, "description": "Traditional baked wheat balls",     "image": "food_images/dal-baati.jpg"},
    {"id": 3, "name": "Dhokla",           "state": "Gujarat",       "price": 149, "description": "Steamed fermented chickpea snack",  "image": "food_images/dhokla.jpg"},
    {"id": 4, "name": "Misal Pav",        "state": "Maharashtra",   "price": 199, "description": "Spicy sprouted beans with bread",   "image": "food_images/misal-pav.jpg"},
    {"id": 5, "name": "Rajma Chawal",     "state": "Uttarakhand",   "price": 149, "description": "Kidney beans curry with rice",      "image": "food_images/rajma-chawal.jpg"},
    {"id": 6, "name": "Idli",             "state": "Karnataka",     "price": 299, "description": "Soft steamed rice cakes",           "image": "food_images/idili.jpg"},
    {"id": 7, "name": "Litti Chokha",     "state": "Bihar",         "price": 149, "description": "Roasted wheat balls with veggies",  "image": "food_images/litti-chokha.jpg"},
    {"id": 8, "name": "Awadhi Biryani",   "state": "Uttar Pradesh", "price": 199, "description": "Slow cooked aromatic rice",         "image": "food_images/awadhi-biryani.jpg"},
]   
     
        for food_data in foods:
            food, created = Food.objects.get_or_create(
                id=food_data["id"],
                defaults={
                    "name":        food_data["name"],
                    "state":       food_data["state"],
                    "price":       food_data["price"],
                    "description": food_data["description"],
                    "image":       food_data["image"],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Added: {food.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  Already exists: {food.name}"))

        self.stdout.write(self.style.SUCCESS("\n🎉 All foods seeded successfully!"))