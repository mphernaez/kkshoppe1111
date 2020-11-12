import uuid
from django.db import models

# Create your models here.
class Item(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(default='', max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=0)
    code = models.CharField(default='', max_length=6)
    group = models.CharField(default='', max_length=100, blank=True)
    price = models.FloatField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:6].upper()
        super(Item, self).save(*args, **kwargs)

    def filter_group(name):
        return Item.objects.filter(group=name)

    def filter_status(status):
        if status == 'available':
            return Item.objects.filter(quantity__gte=1)
        elif status == 'unavailable':
            return Item.objects.filter(quantity=0)

    def get_orders(self):
        order_items = OrderItem.objects.filter(item=self)
        orders = []
        for order_item in order_items:
            orders.append(
                order_item.order
            )
        orders = list(set(orders))
        return orders


class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(default='', max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    code = models.CharField(default='', max_length=6)
    status = models.IntegerField(default=0) # 0 - pending, 1 - confirmed, 2 - paid
    additional_fee = models.FloatField(default=0)
    shipping = models.IntegerField(default=0) # 0 - Pickup, 1 - Davao, 2 - Mindanao, 3 - Visayas, 4 - Luzon 
    shipping_address = models.CharField(default='', max_length=200)
    payment_method = models.IntegerField(default=0) # 0 - PayMaya, 1 - GCash, 2 - Union Bank, 3 - Palawan Express, 4 - On Pickup, 5 - COD
    safekeeping = models.IntegerField(default=0) # 0 - None, 1 - Paper Envelope, 2 - Bubble wrapped, 3 - Gift wrapped, 4 - P & B
    date_paid = models.DateTimeField(blank=True, auto_now_add=True)
    email = models.CharField(default='', max_length=200)
    contact = models.CharField(default='0', max_length=10)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:6].upper()
        super(Order, self).save(*args, **kwargs)

    def get_order_items(self):
        order_items = OrderItem.objects.filter(order=self, status=1)
        return order_items

    def get_items(self):
        order_items = self.get_order_items()
        items = []
        for order_item in order_items:
            items.append(
                order_item.item
            )
        return items

    def get_total(self):
        items = self.get_order_items()
        total = 0
        for item in items:
            total = total + item.quantity * item.item.price
        return total

class OrderItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    # 0 - pending
    # 1 - confirmed