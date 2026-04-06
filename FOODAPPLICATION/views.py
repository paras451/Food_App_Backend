from django.conf import settings
from django.shortcuts import render
import razorpay
from rest_framework.response import Response
from rest_framework import status
from FOODAPPLICATION.models import *
from FOODAPPLICATION.serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# from foodapp.config import settingsAny
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# Create your views here.


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    try:
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error default": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    
    print("Received data:", request.data)
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(username=email, password=password)
        

        if user:
            refresh = RefreshToken.for_user(user)
            
            cart = Cart.objects.filter(user=user).first()
            if cart:
                CartItem.objects.filter(cart=cart).delete()
            
            return Response({"message": "Login successful", "email": user.email,"access":str(refresh.access_token), "refresh": str(refresh)}, status=200)

        return Response({"error": "Invalid credentials"}, status=400)

    return Response(serializer.errors, status=400)


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
     # ← Get current items from frontend
    frontend_items = request.data.get("items", [])
    
    if frontend_items:
        # Clear old cart items
        CartItem.objects.filter(cart=cart).delete()
        
        # Add only current frontend items
        for fi in frontend_items:
            try:
                food = Food.objects.get(id=fi["id"])
                CartItem.objects.create(
                    cart=cart,
                    food=food,
                    quantity=fi["quantity"]
                )
            except Food.DoesNotExist:
                pass
    items = CartItem.objects.filter(cart=cart).select_related("food")
    
    print("User:", request.user)                # ← add
    print("Cart:", cart)                        # ← add
    print("Cart items count:", items.count())   # ← add

    if not items.exists():
        return Response(
            {"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST
        )

    total = sum(item.food.price * item.quantity for item in items)
    amount_in_paise = total * 100

    try:
        rz_order = client.order.create(
            {
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": f"receipt_user_{request.user.id}",
                "payment_capture": 1,
            }
        )
        print("Razorpay order:", rz_order) 

        Order.objects.create(
            user=request.user,
            razorpay_order_id=rz_order["id"],
            amount=total,
            is_paid=False,
        )

        try:
            profile = UserProfile.objects.get(user=request.user)
            user_name = profile.fullName
            user_mobile = profile.mobile_number
        except UserProfile.DoesNotExist:
            user_name = request.user.username
            user_mobile = ""

        return Response(
            {
                "order_id": rz_order["id"],
                "amount": rz_order["amount"],
                "currency": rz_order["currency"],
                "key": settings.RAZORPAY_KEY_ID,
                 "description": ", ".join(        
        f"{item.food.name} x{item.quantity}" for item in items
    ),
                "prefill": {
                    "name": user_name,
                    "email": request.user.email,
                    "contact": user_mobile,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    payment_id = request.data.get("razorpay_payment_id")
    order_id = request.data.get("razorpay_order_id")
    signature = request.data.get("razorpay_signature")

    if not all([payment_id, order_id, signature]):
        return Response(
            {"error": "Missing payment details"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
        )

        order = Order.objects.get(
            razorpay_order_id=order_id, user=request.user
        )
        order.is_paid = True
        order.save()

        cart=Cart.objects.filter(user=request.user).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()

        return Response(
            {
                "status": "Payment successful",
                "order_id": order.id,
                "amount": order.amount,
            }
        )

    except razorpay.errors.SignatureVerificationError:
        return Response(
            {"error": "Invalid payment signature"}, status=status.HTTP_400_BAD_REQUEST
        )

    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    food_id = request.data.get("food_id")

    try:
        food = Food.objects.get(id=food_id)
    except Food.DoesNotExist:
        return Response({"error": "Food item not found"}, status=404)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, food=food)

    if not created:
        item.quantity += 1
        item.save()

    return Response({"message": f"{food.name} added to cart"}, status=200)    
      

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decrease_cart_item(request):
    food_id = request.data.get("food_id")

    try:
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(cart=cart, food_id=food_id)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            return Response({"message": "Quantity decreased"})
        else:
            item.delete()
            return Response({"message": "Item removed"})
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({"error": "Item not found"}, status=404)
    
    
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_cart_item_by_food(request, food_id):
    try:
        cart = Cart.objects.get(user=request.user)
        item = CartItem.objects.get(cart=cart, food_id=food_id)
        item.delete()
        return Response({"message": "Item removed"})
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response({"error": "Item not found"}, status=404)    
    
@api_view(["GET"])
@permission_classes([AllowAny])
def food_list(request):
    foods = Food.objects.all()
    serializer = FoodSerializer(foods, many=True, context={"request": request})
    return Response(serializer.data)    