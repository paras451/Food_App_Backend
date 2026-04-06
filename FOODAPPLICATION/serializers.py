from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from .models import CartItem, Food, Order, UserProfile


class RegisterSerializer(serializers.Serializer):

    fullName = serializers.CharField(max_length=100)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="This email is already taken."
            )
        ]
    )

    mobile_number = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=UserProfile.objects.all(),
                message="This mobile number is already taken."
            )
        ]
    )

    password = serializers.CharField(min_length=6, write_only=True)

    def create(self, validated_data):

        # Create User
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        # Create Profile
        UserProfile.objects.create(
            user=user,
            fullName=validated_data["fullName"],
            mobile_number=validated_data["mobile_number"]
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

## Food serializer   
class FoodSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # returns full image URL

    class Meta:
        model = Food
        fields = ["id", "name", "description", "price", "state", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None 
    
    
## Cart Serializer
class CartItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)
    food_id=serializers.IntegerField(write_only=True)
    subtotal=serializers.SerializerMethodField()
    
    class Meta:
        model=CartItem
        fields="__all__"
        
    def get_subtotal(self, obj):
        return obj.food.price * obj.quantity  
      

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "razorpay_order_id", "amount", "is_paid", "created_at"]        


        