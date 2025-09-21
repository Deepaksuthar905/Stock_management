from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Stock, Order, Trade, UserHolding
from .serializers import StockSerializer, OrderSerializer, TradeSerializer, UserHoldingSerializer, UserRegisterSerializer
from .services import match_orders
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegisterSerializer



class UserLoginView(APIView):
    permission_classes = []  
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user:
           
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "balance": str(user.balance)
            })
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )


# Stocks
class StockListCreateView(generics.ListCreateAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

# Orders (list + create). 
class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().order_by("-timestamp")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       
        return Order.objects.filter(user=self.request.user).order_by("-timestamp")


    def create(self, request, *args, **kwargs):
       
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                
                order = serializer.save(
                    user=request.user,
                    remaining_quantity=serializer.validated_data["quantity"]
                )
                
               
                match_orders(order)
                
                
                headers = self.get_success_headers(serializer.data)
                return Response(
                    OrderSerializer(order, context={'request': request}).data,
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
                
            except Exception as e:
                
                return Response(
                    {"error": f"Order creation failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
           
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Trades
class TradeListView(generics.ListAPIView):
    queryset = Trade.objects.all().order_by("-timestamp")
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        
        return Trade.objects.filter(
            Q(buy_order__user=self.request.user) | Q(sell_order__user=self.request.user)
        ).order_by("-timestamp")

# Holdings
class UserHoldingListView(generics.ListAPIView):
    queryset = UserHolding.objects.all()
    serializer_class = UserHoldingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       
        return UserHolding.objects.filter(user=self.request.user)

# Search endpoint: id exact or name prefix (case-insensitive)
@api_view(["GET"])
def search_stock(request):
    q = request.GET.get("q", "").strip()
    if q == "":
        return Response({"detail": "query param 'q' required"}, status=status.HTTP_400_BAD_REQUEST)

    # if numeric => search by id
    if q.isdigit():
        stocks = Stock.objects.filter(id=int(q))
    else:
        # prefix search: behaves like trie startswith
        stocks = Stock.objects.filter(name__istartswith=q)
    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data)