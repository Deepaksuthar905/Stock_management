from django.db import transaction
from .models import Order, Trade, UserHolding
from decimal import Decimal

def update_holdings_after_trade(buyer, seller, stock, qty, price):
    """Update buyer and seller holdings atomically (caller should be in transaction)."""
    total_cost = price * qty
    if buyer.balance < total_cost:
        raise ValueError(f"Buyer has insufficient balance. Required: {total_cost}, Available: {buyer.balance}")
    
    buyer.balance -= total_cost
    buyer.save()

    
    seller.balance += total_cost
    seller.save()
    
    holding, created = UserHolding.objects.get_or_create(
        user=buyer, stock=stock, defaults={"quantity": 0, "avg_price": price}
    )
    if not created:
        
        total_cost = (holding.avg_price * holding.quantity) + (Decimal(price) * qty)
        new_qty = holding.quantity + qty
        holding.avg_price = (total_cost / new_qty).quantize(Decimal("0.01"))
        holding.quantity = new_qty
    else:
        holding.quantity = qty
        holding.avg_price = Decimal(price).quantize(Decimal("0.01"))
    holding.save()

   
    try:
        seller_holding = UserHolding.objects.get(user=seller, stock=stock)
        if seller_holding.quantity < qty:
           
            seller_holding.quantity = 0
            seller_holding.delete()
        else:
            seller_holding.quantity -= qty
            if seller_holding.quantity == 0:
                seller_holding.delete()
            else:
                seller_holding.save()
    except UserHolding.DoesNotExist:
       
        pass

def match_orders(new_order):
    """
    Core matching engine.
    new_order should be saved already (with remaining_quantity set).
    """
    from .models import User

    if new_order.remaining_quantity == 0:
        return
    
    if new_order.order_type == Order.BUY:
        total_cost = new_order.price * new_order.quantity
        if new_order.user.balance < total_cost:
          
            new_order.status = Order.PENDING 
            new_order.remaining_quantity = new_order.quantity
            new_order.save()
            return
        

    if new_order.order_type == Order.BUY:
        opposite_qs = Order.objects.filter(
            stock=new_order.stock,
            order_type=Order.SELL,
            price__lte=new_order.price,
            status__in=[Order.PENDING, Order.PARTIAL],
        ).order_by("price", "timestamp")
    else:
        opposite_qs = Order.objects.filter(
            stock=new_order.stock,
            order_type=Order.BUY,
            price__gte=new_order.price,
            status__in=[Order.PENDING, Order.PARTIAL],
        ).order_by("-price", "timestamp")

    with transaction.atomic():
        for opp in opposite_qs.select_for_update():
            if new_order.remaining_quantity == 0:
                break

            matched_qty = min(new_order.remaining_quantity, opp.remaining_quantity)
           
            trade_price = opp.price

           
            Trade.objects.create(
                buy_order=new_order if new_order.order_type == Order.BUY else opp,
                sell_order=opp if new_order.order_type == Order.BUY else new_order,
                stock=new_order.stock,
                price=trade_price,
                quantity=matched_qty,
            )

           
            new_order.remaining_quantity -= matched_qty
            opp.remaining_quantity -= matched_qty

            opp.status = Order.COMPLETED if opp.remaining_quantity == 0 else Order.PARTIAL
            opp.save()

            new_order.status = Order.COMPLETED if new_order.remaining_quantity == 0 else Order.PARTIAL
            new_order.save()

           
            if new_order.order_type == Order.BUY:
                buyer = new_order.user
                seller = opp.user
            else:
                buyer = opp.user
                seller = new_order.user

            update_holdings_after_trade(buyer, seller, new_order.stock, matched_qty, trade_price)
