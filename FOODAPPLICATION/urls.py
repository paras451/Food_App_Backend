from django.urls import path
from FOODAPPLICATION.views import *

urlpatterns = [
    path("register/", register_user, name="register_user"),
    path("login/", login_user, name="login_user"),
    path("create_order/", create_order, name="create_order"),
    path("verify_payment/", verify_payment, name="verify_payment"),
    path("add_to_cart/", add_to_cart, name="add_to_cart"),
    path("cart/decrease/",decrease_cart_item),
    path("cart/remove_by_food/<int:food_id>/", remove_cart_item_by_food),
    path("foods/", food_list),

]
  