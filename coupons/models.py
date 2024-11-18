from decimal import Decimal

from django.db import models
from django.utils import timezone


# Coupon Model
class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('Percentage', 'Percentage'),
        ('Amount', 'Amount'),
    )
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    expiration_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.code

    def is_valid(self):
        """
        Check if the coupon is valid (active, not expired, and under usage limit).
        """
        if not self.is_active:
            return False
        if self.expiration_date < timezone.now():
            return False
        if self.used_count >= self.usage_limit:
            return False
        return True

    def apply_discount(self, order_total):
        """
        Apply the discount to the given order total.
        """
        if self.discount_type == 'percentage':
            if isinstance(order_total, Decimal):
                discount = Decimal(str(self.discount_value / 100)) * order_total
            else:
                discount = self.discount_value / 100 * order_total
        else:
            discount = self.discount_value

        if discount < 0:
            discount = 0
        return min(discount, order_total)


