# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from .models import Stock, Order, Trade, UserHolding
# from .services import match_orders

# User = get_user_model()

# class MatchingEngineTests(TestCase):
#     def setUp(self):
#         self.buyer = User.objects.create_user(username="buyer", password="pass")
#         self.seller = User.objects.create_user(username="seller", password="pass")
#         self.stock = Stock.objects.create(name="AAPL", current_price=100)

#     def test_exact_order_match(self):
#         buy = Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
#                                    price=100, quantity=1000, remaining_quantity=1000)
#         sell = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
#                                     price=100, quantity=1000, remaining_quantity=1000)
#         match_orders(buy)

#         buy.refresh_from_db()
#         sell.refresh_from_db()
#         self.assertEqual(buy.status, Order.COMPLETED)
#         self.assertEqual(sell.status, Order.COMPLETED)
#         trades = Trade.objects.filter(buy_order=buy, sell_order=sell)
#         self.assertEqual(trades.count(), 1)
#         self.assertEqual(trades.first().quantity, 1000)

#     def test_partial_order_match(self):
#         buy = Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
#                                    price=100, quantity=1000, remaining_quantity=1000)
#         sell = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
#                                     price=100, quantity=600, remaining_quantity=600)
#         match_orders(buy)
#         buy.refresh_from_db()
#         sell.refresh_from_db()
#         self.assertEqual(buy.remaining_quantity, 400)
#         self.assertEqual(buy.status, Order.PARTIAL)
#         self.assertEqual(sell.status, Order.COMPLETED)

#     def test_timestamp_priority(self):
#         buy = Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
#                                    price=100, quantity=1000, remaining_quantity=1000)
#         # two sellers same price but different created order timestamps
#         sell1 = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
#                                     price=100, quantity=500, remaining_quantity=500)
#         sell2 = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
#                                     price=100, quantity=500, remaining_quantity=500)
#         match_orders(buy)
#         sell1.refresh_from_db()
#         sell2.refresh_from_db()
#         # sell1 should be filled (or partially), then sell2
#         self.assertTrue(sell1.status in [Order.COMPLETED, Order.PARTIAL])
#         # after matching, total sold should be 1000 if two sellers filled
#         buy.refresh_from_db()
#         self.assertIn(buy.status, [Order.COMPLETED, Order.PARTIAL])

#     def test_bulk_ordering_small_scale(self):
#         """
#         Bulk test kept moderate here for CI speed. Increase loops to stress test locally:
#         e.g., n = 10000 (Beware long runtime).
#         """
#         n = 500  # increase to 10000 for heavy stress locally if machine can handle it
#         # create matching buy+sell pairs
#         for i in range(n):
#             Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
#                                  price=100, quantity=100, remaining_quantity=100)
#             Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
#                                  price=100, quantity=100, remaining_quantity=100)
#         # run matching on all buys
#         buys = Order.objects.filter(order_type=Order.BUY)
#         for b in buys:
#             match_orders(b)
#         trades_count = Trade.objects.count()
#         self.assertTrue(trades_count >= n)  # at least n trades created



    

#     def test_insufficient_balance(self):
#     # Buyer with low balance
#         self.buyer.balance = 50
#         self.buyer.save()

#         buy = Order.objects.create(
#             user=self.buyer, 
#             stock=self.stock, 
#             order_type=Order.BUY,
#             price=100, 
#             quantity=1, 
#             remaining_quantity=1
#         )
#         match_orders(buy)
#         buy.refresh_from_db()

#         self.assertEqual(buy.status, Order.PENDING)  # order not matched because of no money
#         self.assertEqual(self.buyer.balance, 50)     # balance unchanged

    



from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Stock, Order, Trade, UserHolding
from .services import match_orders

User = get_user_model()

class MatchingEngineTests(TestCase):
    def setUp(self):
       
        self.buyer = User.objects.create_user(
            username="buyer", 
            password="pass",
            balance=Decimal("100000.00") 
        )
        self.seller = User.objects.create_user(
            username="seller", 
            password="pass",
            balance=Decimal("100000.00") 
        )
        self.stock = Stock.objects.create(name="AAPL", current_price=100)

    def test_exact_order_match(self):
        buy = Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
                                   price=100, quantity=1000, remaining_quantity=1000)
        sell = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
                                    price=100, quantity=1000, remaining_quantity=1000)
        match_orders(buy)

        buy.refresh_from_db()
        sell.refresh_from_db()
        self.buyer.refresh_from_db() 
        self.seller.refresh_from_db() 
        
        self.assertEqual(buy.status, Order.COMPLETED)
        self.assertEqual(sell.status, Order.COMPLETED)
        trades = Trade.objects.filter(buy_order=buy, sell_order=sell)
        self.assertEqual(trades.count(), 1)
        self.assertEqual(trades.first().quantity, 1000)
        
       
        self.assertEqual(self.buyer.balance, Decimal("0.00")) 
        self.assertEqual(self.seller.balance, Decimal("200000.00")) 

    def test_partial_order_match(self):
        buy = Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
                                   price=100, quantity=1000, remaining_quantity=1000)
        sell = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
                                    price=100, quantity=600, remaining_quantity=600)
        match_orders(buy)
        
        buy.refresh_from_db()
        sell.refresh_from_db()
        self.buyer.refresh_from_db()
        self.seller.refresh_from_db()
        
        self.assertEqual(buy.remaining_quantity, 400)
        self.assertEqual(buy.status, Order.PARTIAL)
        self.assertEqual(sell.status, Order.COMPLETED)
        
        # Balance changes check karein
        self.assertEqual(self.buyer.balance, Decimal("40000.00")) 
        self.assertEqual(self.seller.balance, Decimal("160000.00")) 

    def test_timestamp_priority(self):
        buy = Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
                                   price=100, quantity=1000, remaining_quantity=1000)
       
        sell1 = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
                                    price=100, quantity=500, remaining_quantity=500)
        sell2 = Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
                                    price=100, quantity=500, remaining_quantity=500)
        match_orders(buy)
        
        sell1.refresh_from_db()
        sell2.refresh_from_db()
        self.buyer.refresh_from_db()
        self.seller.refresh_from_db()
        
       
        self.assertTrue(sell1.status in [Order.COMPLETED, Order.PARTIAL])
        
        buy.refresh_from_db()
        self.assertIn(buy.status, [Order.COMPLETED, Order.PARTIAL])
        
        
        self.assertEqual(self.buyer.balance, Decimal("0.00"))  # All money spent
        self.assertEqual(self.seller.balance, Decimal("200000.00"))  # All money received

    def test_bulk_ordering_small_scale(self):
        """
        Bulk test kept moderate here for CI speed. Increase loops to stress test locally:
        e.g., n = 10000 (Beware long runtime).
        """
        n = 500  # increase to 10000 for heavy stress locally if machine can handle it
        
        # Pehle balance sufficient hai ensure karein
        self.buyer.balance = Decimal("10000000.00")  # 10 million
        self.buyer.save()
        
        # create matching buy+sell pairs
        for i in range(n):
            Order.objects.create(user=self.buyer, stock=self.stock, order_type=Order.BUY,
                                 price=100, quantity=100, remaining_quantity=100)
            Order.objects.create(user=self.seller, stock=self.stock, order_type=Order.SELL,
                                 price=100, quantity=100, remaining_quantity=100)
        
        # run matching on all buys
        buys = Order.objects.filter(order_type=Order.BUY)
        for b in buys:
            match_orders(b)
        
        trades_count = Trade.objects.count()
        self.assertTrue(trades_count >= n)  # at least n trades created

    def test_insufficient_balance(self):
        # Buyer with low balance
        self.buyer.balance = Decimal("50.00")  # Decimal use karein
        self.buyer.save()

        buy = Order.objects.create(
            user=self.buyer, 
            stock=self.stock, 
            order_type=Order.BUY,
            price=100, 
            quantity=1, 
            remaining_quantity=1
        )
        
        # Create a matching sell order
        sell = Order.objects.create(
            user=self.seller, 
            stock=self.stock, 
            order_type=Order.SELL,
            price=100, 
            quantity=1, 
            remaining_quantity=1
        )
        
        match_orders(buy)
        
        buy.refresh_from_db()
        sell.refresh_from_db()
        self.buyer.refresh_from_db()

        self.assertEqual(buy.status, Order.PENDING)  # order not matched because of no money
        self.assertEqual(self.buyer.balance, Decimal("50.00"))  # balance unchanged
        self.assertEqual(sell.status, Order.PENDING)  # sell order should also remain pending