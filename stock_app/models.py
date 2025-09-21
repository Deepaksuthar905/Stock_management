from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.core.validators import EmailValidator

class User(AbstractUser):
    email = models.EmailField(
        unique=True, 
        validators=[EmailValidator()],
        error_messages={
            'unique': "A user with that email already exists.",
        }
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("100000.00"))
    # pass
    def __str__(self):
        return self.username

class Stock(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    def get_identifier(self):
      
        if hasattr(self, 'symbol'):
            return self.symbol
        return self.name
    
    def __str__(self):
        return self.get_identifier()



class Order(models.Model):
    BUY = "BUY"
    SELL = "SELL"
    ORDER_TYPES = [(BUY, "Buy"), (SELL, "Sell")]

    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    COMPLETED = "COMPLETED"
    STATUS_CHOICES = [(PENDING, "Pending"), (PARTIAL, "Partial"), (COMPLETED, "Completed")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_type} {self.quantity} {self.stock.name} @ {self.price} ({self.status})"

class Trade(models.Model):
    buy_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="buy_trades")
    sell_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="sell_trades")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade {self.id}: {self.quantity} {self.stock.name} @ {self.price}"

class UserHolding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    avg_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("user", "stock")

    def __str__(self):
        return f"{self.user.username} holding {self.quantity} {self.stock.name}"
