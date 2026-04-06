from django.contrib import admin

# Register your models here.


from .models import Cart, CartItem, Food, Order, UserProfile

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Food)
admin.site.register(Order)
admin.site.register(UserProfile)