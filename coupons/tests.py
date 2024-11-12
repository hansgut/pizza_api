from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from .models import Coupon
from django.contrib.auth.models import User
import datetime


class CouponModelTestCase(TestCase):

    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="DISCOUNT10",
            description="10% off your order",
            discount_type="percentage",
            discount_value=10,
            expiration_date=timezone.now() + datetime.timedelta(days=7),
            is_active=True,
            usage_limit=5
        )

    def test_coupon_creation(self):
        """
        Test that a coupon is created correctly.
        """
        self.assertEqual(self.coupon.code, "DISCOUNT10")
        self.assertEqual(self.coupon.discount_value, 10)
        self.assertTrue(self.coupon.is_valid())

    def test_coupon_expiration(self):
        """
        Test that the coupon is invalid if it is expired.
        """
        self.coupon.expiration_date = timezone.now() - datetime.timedelta(days=1)
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())

    def test_coupon_usage_limit(self):
        """
        Test that the coupon is invalid if it exceeds the usage limit.
        """
        self.coupon.used_count = 5
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())

    def test_apply_discount_percentage(self):
        """
        Test applying a percentage discount.
        """
        order_total = 100
        discount = self.coupon.apply_discount(order_total)
        self.assertEqual(discount, 10)

    def test_apply_discount_amount(self):
        """
        Test applying a fixed amount discount.
        """
        self.coupon.discount_type = "amount"
        self.coupon.discount_value = 15
        self.coupon.save()
        order_total = 100
        discount = self.coupon.apply_discount(order_total)
        self.assertEqual(discount, 15)

    def test_apply_discount_exceeds_total(self):
        """
        Test that the discount does not exceed the order total.
        """
        self.coupon.discount_type = "amount"
        self.coupon.discount_value = 150
        self.coupon.save()
        order_total = 100
        discount = self.coupon.apply_discount(order_total)
        self.assertEqual(discount, 100)  # The discount should not exceed the total


class CouponAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

        self.coupon = Coupon.objects.create(
            code="SAVE20",
            description="Save 20 dollars on your order",
            discount_type="amount",
            discount_value=20,
            expiration_date=timezone.now() + datetime.timedelta(days=7),
            is_active=True,
            usage_limit=3
        )

        self.apply_coupon_url = reverse('apply-coupon')

    def test_apply_coupon_valid(self):
        """
        Test applying a valid coupon.
        """
        data = {"code": "SAVE20"}
        response = self.client.post(self.apply_coupon_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["discount_value"], 20)

    def test_apply_coupon_invalid(self):
        """
        Test applying an invalid or expired coupon.
        """
        self.coupon.expiration_date = timezone.now() - datetime.timedelta(days=1)
        self.coupon.save()
        data = {"code": "SAVE20"}
        response = self.client.post(self.apply_coupon_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This coupon is not valid.", response.data["code"])

    def test_apply_coupon_usage_limit_reached(self):
        """
        Test applying a coupon that has reached its usage limit.
        """
        self.coupon.used_count = 3
        self.coupon.save()
        data = {"code": "SAVE20"}
        response = self.client.post(self.apply_coupon_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This coupon is not valid.", response.data["code"])
