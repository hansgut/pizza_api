from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Address
from menu.models import MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping
from coupons.models import Coupon
from delivery.models import Driver
from .helpers import calculate_net_and_tax


ORDER_STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Preparing', 'Preparing'),
    ('Out for Delivery', 'Out for Delivery'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00)])
    netto_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.00)])
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

    def apply_coupon(self):
        if self.coupon and self.coupon.is_valid():
            discount = self.coupon.apply_discount(self.total_amount)
            self.discount_amount = discount
            self.netto_total, self.tax_amount = calculate_net_and_tax(self.total_amount - discount)
            self.save()

    def unapply_coupon(self):
        self.discount_amount = 0.00
        self.netto_total, self.tax_amount = calculate_net_and_tax(self.total_amount)
        self.save()

    def total_price_with_discount(self):
        return self.total_amount - self.discount_amount


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    is_pizza = models.BooleanField(default=False)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Item #{self.id} of Order #{self.order.id}"


class OrderItemPizza(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='pizza')
    size = models.ForeignKey(PizzaSize, on_delete=models.SET_NULL, null=True)
    crust_type = models.ForeignKey(CrustType, on_delete=models.SET_NULL, null=True)
    sauce = models.ForeignKey(Sauce, on_delete=models.SET_NULL, null=True)
    cheese = models.ForeignKey(Cheese, on_delete=models.SET_NULL, null=True)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"Pizza for Item #{self.order_item.id}"


class OrderItemPizzaTopping(models.Model):
    order_item_pizza = models.ForeignKey(OrderItemPizza, on_delete=models.CASCADE, related_name='toppings')
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE)
    portion = models.CharField(max_length=10, choices=[('Normal', 'Normal'), ('Extra', 'Extra')])
    side = models.CharField(max_length=10,
                            choices=[('Whole', 'Whole'), ('Left Half', 'Left Half'), ('Right Half', 'Right Half')])

    def __str__(self):
        return f"{self.topping.name} on {self.side} of Pizza #{self.order_item_pizza.id}"
