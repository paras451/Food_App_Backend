from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


# Food Model
class Food(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    state = models.CharField(max_length=100)
    image = models.ImageField(upload_to="food_images/")

    # cart model


class CartItem(models.Model):
 
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    food = models.ForeignKey("Food", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


# Order model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, unique=True)
    fullName = models.CharField(max_length=255)

    def __str__(self):
        return self.fullName
