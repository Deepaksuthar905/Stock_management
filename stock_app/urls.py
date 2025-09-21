from django.urls import path
from .views import StockListCreateView, OrderListCreateView, TradeListView, UserHoldingListView, search_stock
from . import views
from rest_framework.authtoken import views as auth_views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', auth_views.obtain_auth_token, name='login'),
    path("stocks/", StockListCreateView.as_view(), name="stocks"),
    path("stocks/search/", search_stock, name="stock-search"),
    path("orders/", OrderListCreateView.as_view(), name="orders"),
    path("trades/", TradeListView.as_view(), name="trades"),
    path("holdings/", UserHoldingListView.as_view(), name="holdings"),
]
