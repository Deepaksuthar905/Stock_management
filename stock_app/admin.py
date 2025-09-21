from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Stock, Order, Trade, UserHolding

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "current_price", "timestamp")
    search_fields = ("name",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "stock", "order_type", "price", "quantity", "remaining_quantity", "status", "timestamp")
    list_filter = ("order_type", "status", "stock")
    search_fields = ("user__username", "stock__name")

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("id", "stock", "price", "quantity", "timestamp")
    search_fields = ("stock__name",)

@admin.register(UserHolding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "stock", "quantity", "avg_price")
    search_fields = ("user__username", "stock__name")
