from rest_framework import serializers
from .models import Stock, Order, Trade, UserHolding
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {
                'validators': [EmailValidator()],
            },
            'username': {
                'min_length': 3,
                'max_length': 150,
            }
        }
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user





class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"

    def validate_name(self, value):
        if Stock.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Stock with this name already exists.")
        return value



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = ("user", "remaining_quantity", "status", "timestamp")

    def validate(self, data):
        
        request = self.context.get('request')
        user = request.user if request else None
        
        
        if data["price"] <= 0:
            raise serializers.ValidationError("Price must be positive.")
        
        if data["quantity"] <= 0:
            raise serializers.ValidationError("Quantity must be positive.")
        
        
        if data["order_type"] == "BUY" and user:
            total_cost = data["price"] * data["quantity"]
            if user.balance < total_cost:
                raise serializers.ValidationError(
                    f"Insufficient balance. Required: {total_cost:.2f}, Available: {user.balance:.2f}"
                )
        
        
        if data["order_type"] == "SELL" and user:
            try:
                stock_identifier = data["stock"].get_identifier()
                
                holding = UserHolding.objects.get(user=user, stock=data["stock"])
                if holding.quantity < data["quantity"]:
                    raise serializers.ValidationError(
                        f"Insufficient shares. You have only {holding.quantity} shares of {stock_identifier}"
                    )
            except UserHolding.DoesNotExist:
                stock_identifier = data["stock"].get_identifier()
                raise serializers.ValidationError(
                    f"You don't own any shares of {stock_identifier}"
                )
        
        return data


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = "__all__"

class UserHoldingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHolding
        fields = "__all__"
