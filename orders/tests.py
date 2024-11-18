from decimal import Decimal, ROUND_HALF_UP

from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Address
from orders.models import Order, OrderItem
from menu.models import MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping
from coupons.models import Coupon
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime


class OrderAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        # Create menu items and address
        self.menu_item = MenuItem.objects.create(name="Pizza", price=Decimal('20.00'))
        self.size = PizzaSize.objects.create(name="Large", diameter=14, base_price=Decimal('0.00'))
        self.crust_type = CrustType.objects.create(name="Thin Crust", price=Decimal('0.00'))
        self.sauce = Sauce.objects.create(name="Tomato Sauce", price=Decimal('0.00'))
        self.cheese = Cheese.objects.create(name="Mozzarella", price=Decimal('0.00'))
        self.topping = Topping.objects.create(name="Pepperoni", price=Decimal('2.00'))

        self.address = Address.objects.create(
            customer=self.user,
            street="123 Pizza Street",
            city="Pizza City",
            zip_code="12345"
        )

        self.coupon = Coupon.objects.create(
            code="SAVE10",
            discount_type="percentage",
            discount_value=10,
            expiration_date=timezone.now() + datetime.timedelta(days=7),
            is_active=True
        )

        self.value_coupon = Coupon.objects.create(
            code="VALUE10",
            discount_type="amount",
            discount_value=10,
            expiration_date=timezone.now() + datetime.timedelta(days=7),
            is_active=True
        )

        # Initialize order amounts using Decimal for precision
        self.order_total_amount = Decimal('20.00')
        self.tax_rate = Decimal('0.08')  # 8% tax rate

        # Calculate netto_total and tax_amount
        self.netto_total = (self.order_total_amount / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        self.tax_amount = (self.order_total_amount - self.netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        self.order = Order.objects.create(
            customer=self.user,
            delivery_address=self.address,
            total_amount=self.order_total_amount,
            netto_total=self.netto_total,
            tax_amount=self.tax_amount
        )

    def test_order_creation_with_address(self):
        """
        Test creating an order with a saved address.
        """
        url = reverse('order-list')
        data = {
            "customer": self.user.id,
            "delivery_address": self.address.id,
            "items": [
                {"menu_item": self.menu_item.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Order.objects.last().delivery_address, self.address)

    def test_create_custom_pizza_item(self):
        """
        Test creating a custom pizza item with size, crust, sauce, cheese, and toppings.
        """
        url = reverse('order-list')
        data = {
            "customer": self.user.id,
            "delivery_address": self.address.id,
            "items": [
                {
                    "menu_item": self.menu_item.id,
                    "quantity": 1,
                    "is_pizza": True,
                    "pizza": {
                        "size": self.size.id,
                        "crust_type": self.crust_type.id,
                        "sauce": self.sauce.id,
                        "cheese": self.cheese.id,
                        "toppings": [
                            {"topping": self.topping.id, "portion": "Extra", "side": "Whole"}
                        ]
                    }
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

        # Verify the created order item
        order_item = OrderItem.objects.last()

        # Calculate the expected price of the custom pizza
        topping_price = self.topping.price * Decimal('1.5')  # Extra portion is 1.5x price
        pizza_price = (
            self.menu_item.price +
            self.size.base_price +
            self.crust_type.price +
            self.sauce.price +
            self.cheese.price +
            topping_price
        )

        # Assertions
        self.assertEqual(order_item.unit_price, pizza_price)
        self.assertEqual(order_item.total_price, pizza_price)
        self.assertEqual(order_item.quantity, 1)

    def test_apply_and_unapply_coupon_to_order(self):
        """
        Test applying and unapplying a valid coupon to an order.
        """
        self.order.coupon = self.coupon
        self.order.apply_coupon()
        self.order.save()

        # Calculate expected discount and totals
        discount_amount = (self.order.total_amount * Decimal('0.10')).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        discounted_total = self.order.total_amount - discount_amount
        netto_total = (discounted_total / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        tax_amount = (discounted_total - netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        self.assertEqual(self.order.discount_amount, discount_amount)
        self.assertEqual(self.order.netto_total, netto_total)
        self.assertEqual(self.order.tax_amount, tax_amount)

        # Unapply coupon
        self.order.unapply_coupon()
        self.order.save()

        # Recalculate totals without discount
        netto_total = (self.order.total_amount / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        tax_amount = (self.order.total_amount - netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        self.assertEqual(self.order.discount_amount, Decimal('0.00'))
        self.assertEqual(self.order.netto_total, netto_total)
        self.assertEqual(self.order.tax_amount, tax_amount)

    def test_order_status_update(self):
        """
        Test updating the status of an order.
        """
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        data = {"status": "Delivered"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "Delivered")

    def test_retrieve_order(self):
        """
        Test retrieving an order by its ID.
        """
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["customer"], self.user.id)

    def test_negative_quantity_order_item(self):
        """
        Test that creating an OrderItem with a negative quantity is not allowed.
        """
        order_item = OrderItem(
            order=self.order,
            menu_item=self.menu_item,
            quantity=-1,
            unit_price=Decimal('20.00'),
            total_price=Decimal('20.00')
        )
        with self.assertRaises(ValidationError):
            order_item.full_clean()

    def test_two_order_items_and_pizza_via_api(self):
        """
        Test creating two OrderItems and a pizza item via the API.
        """
        cola = MenuItem.objects.create(name="Cola", price=Decimal('5.00'))
        fries = MenuItem.objects.create(name="Fries", price=Decimal('10.00'))
        url = reverse('order-list')
        data = {
            "customer": self.user.id,
            "delivery_address": self.address.id,
            "items": [
                {"menu_item": cola.id, "quantity": 1},
                {"menu_item": fries.id, "quantity": 1},
                {
                    "menu_item": self.menu_item.id,
                    "quantity": 1,
                    "is_pizza": True,
                    "pizza": {
                        "size": self.size.id,
                        "crust_type": self.crust_type.id,
                        "sauce": self.sauce.id,
                        "cheese": self.cheese.id,
                        "toppings": [
                            {"topping": self.topping.id, "portion": "Extra", "side": "Whole"}
                        ]
                    }
                }
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(OrderItem.objects.count(), 3)
        self.assertEqual(OrderItem.objects.filter(is_pizza=True).count(), 1)
        self.assertEqual(OrderItem.objects.filter(is_pizza=False).count(), 2)
        self.assertEqual(OrderItem.objects.last().order.customer, self.user)
        self.assertEqual(OrderItem.objects.last().order.delivery_address, self.address)

        # Calculate expected total amount
        topping_price = self.topping.price * Decimal('1.5')  # Extra portion
        pizza_price = self.menu_item.price + topping_price
        total_amount = cola.price + fries.price + pizza_price

        # Recalculate netto_total and tax_amount
        netto_total = (total_amount / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        tax_amount = (total_amount - netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        order = Order.objects.last()
        self.assertEqual(order.total_amount, total_amount)
        self.assertEqual(order.netto_total, netto_total)
        self.assertEqual(order.tax_amount, tax_amount)

    def test_order_pizzas_with_cola_and_apply_coupon(self):
        """
        Test creating pizzas and a cola item, then applying and unapplying a coupon.
        """
        cola = MenuItem.objects.create(name="Cola", price=Decimal('5.00'))
        url = reverse('order-list')
        data = {
            "customer": self.user.id,
            "delivery_address": self.address.id,
            "items": [
                {
                    "menu_item": self.menu_item.id,
                    "quantity": 2,
                    "is_pizza": True,
                    "pizza": {
                        "size": self.size.id,
                        "crust_type": self.crust_type.id,
                        "sauce": self.sauce.id,
                        "cheese": self.cheese.id,
                        "toppings": [
                            {"topping": self.topping.id, "portion": "Extra", "side": "Whole"}
                        ]
                    }
                },
                {
                    "menu_item": self.menu_item.id,
                    "quantity": 1,
                    "is_pizza": True,
                    "pizza": {
                        "size": self.size.id,
                        "crust_type": self.crust_type.id,
                        "sauce": self.sauce.id,
                        "cheese": self.cheese.id,
                        "toppings": [
                            {"topping": self.topping.id, "portion": "Normal", "side": "Whole"}
                        ]
                    }
                },
                {"menu_item": cola.id, "quantity": 3}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(OrderItem.objects.count(), 3)
        self.assertEqual(OrderItem.objects.filter(is_pizza=True).count(), 2)
        self.assertEqual(OrderItem.objects.filter(is_pizza=False).count(), 1)
        self.assertEqual(OrderItem.objects.last().order.customer, self.user)
        self.assertEqual(OrderItem.objects.last().order.delivery_address, self.address)

        # Calculate expected total amount
        extra_topping_price = self.topping.price * Decimal('1.5')
        normal_topping_price = self.topping.price
        pizza1_price = (self.menu_item.price + extra_topping_price) * 2  # Quantity of 2
        pizza2_price = self.menu_item.price + normal_topping_price
        cola_price = cola.price * 3
        total_amount = pizza1_price + pizza2_price + cola_price

        # Recalculate netto_total and tax_amount
        netto_total = (total_amount / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        tax_amount = (total_amount - netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        order = Order.objects.last()
        self.assertEqual(order.total_amount, total_amount)
        self.assertEqual(order.netto_total, netto_total)
        self.assertEqual(order.tax_amount, tax_amount)

        # Apply coupon
        url = reverse('order-coupon', kwargs={'pk': order.id})
        data = {"coupon": self.coupon.code}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        # Recalculate discount amount
        discount_amount = (order.total_amount * Decimal('0.10')).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        discounted_total = order.total_amount - discount_amount
        new_netto_total = (discounted_total / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        new_tax_amount = (discounted_total - new_netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        order.refresh_from_db()
        self.assertEqual(order.discount_amount, discount_amount)
        self.assertEqual(order.netto_total, new_netto_total)
        self.assertEqual(order.tax_amount, new_tax_amount)
        self.assertEqual(order.total_amount, total_amount)

        # Unapply coupon
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.discount_amount, Decimal('0.00'))
        self.assertEqual(order.netto_total, netto_total)
        self.assertEqual(order.tax_amount, tax_amount)
        self.assertEqual(order.total_amount, total_amount)

        # Apply value coupon

        data = {"coupon": self.value_coupon.code}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)

        discount_amount = Decimal('10.00')
        discounted_total = order.total_amount - discount_amount
        new_netto_total = (discounted_total / (1 + self.tax_rate)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        new_tax_amount = (discounted_total - new_netto_total).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        order.refresh_from_db()

        self.assertEqual(order.discount_amount, Decimal('10.00'))
        self.assertEqual(order.netto_total, new_netto_total)
        self.assertEqual(order.tax_amount, new_tax_amount)
        self.assertEqual(order.total_amount, total_amount)

        # Unapply value coupon
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.discount_amount, Decimal('0.00'))
        self.assertEqual(order.netto_total, netto_total)
        self.assertEqual(order.tax_amount, tax_amount)