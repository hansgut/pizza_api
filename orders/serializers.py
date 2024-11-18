from rest_framework import serializers
from .models import Order, OrderItem, OrderItemPizza, OrderItemPizzaTopping
from menu.models import MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping
from django.contrib.auth.models import User
from accounts.models import Address
from coupons.models import Coupon
from delivery.models import Driver
from decimal import Decimal
from .helpers import calculate_net_and_tax


class OrderItemPizzaToppingSerializer(serializers.ModelSerializer):
    topping = serializers.PrimaryKeyRelatedField(queryset=Topping.objects.all())

    class Meta:
        model = OrderItemPizzaTopping
        fields = ['topping', 'portion', 'side']


class OrderItemPizzaSerializer(serializers.ModelSerializer):
    size = serializers.PrimaryKeyRelatedField(queryset=PizzaSize.objects.all())
    crust_type = serializers.PrimaryKeyRelatedField(queryset=CrustType.objects.all())
    sauce = serializers.PrimaryKeyRelatedField(queryset=Sauce.objects.all())
    cheese = serializers.PrimaryKeyRelatedField(queryset=Cheese.objects.all())
    toppings = OrderItemPizzaToppingSerializer(many=True, required=False)

    class Meta:
        model = OrderItemPizza
        fields = ['size', 'crust_type', 'sauce', 'cheese', 'instructions', 'toppings']


class OrderItemSerializer(serializers.ModelSerializer):
    pizza = OrderItemPizzaSerializer(required=False)
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'unit_price', 'total_price', 'is_pizza', 'pizza', 'instructions']
        read_only_fields = ['unit_price', 'total_price', 'id']

    def create(self, validated_data):
        # Remove 'id' if present
        validated_data.pop('id', None)

        pizza_data = validated_data.pop('pizza', None)
        quantity = validated_data.get('quantity', 1)
        is_pizza = validated_data.get('is_pizza', False)
        menu_item = validated_data['menu_item']
        unit_price = menu_item.price

        # Calculate unit_price and total_price
        if is_pizza and pizza_data:
            size = pizza_data['size']
            crust_type = pizza_data['crust_type']
            sauce = pizza_data['sauce']
            cheese = pizza_data['cheese']
            pizza_from_menu = MenuItem.objects.get(pk=menu_item.id)
            # Base price calculation
            unit_price = pizza_from_menu.price + size.base_price + crust_type.price + sauce.price + cheese.price

            # Toppings price calculation
            toppings_data = pizza_data.get('toppings', [])
            for topping_data in toppings_data:
                topping = topping_data['topping']
                portion = topping_data.get('portion', 'Normal')
                topping_price = topping.price * Decimal(1.5) if portion == 'Extra' else topping.price
                unit_price += topping_price

        total_price = unit_price * quantity
        validated_data['unit_price'] = unit_price
        validated_data['total_price'] = total_price

        # Associate the order with the order item
        order = self.context.get('order')
        validated_data['order'] = order

        # Remove 'id' from validated_data before creating the OrderItem
        validated_data.pop('id', None)
        order_item = OrderItem.objects.create(**validated_data)

        # Handle pizza data if present
        if is_pizza and pizza_data:
            # Prepare data for OrderItemPizza
            pizza_data_clean = {
                'order_item': order_item,
                'size': size,
                'crust_type': crust_type,
                'sauce': sauce,
                'cheese': cheese,
                'instructions': pizza_data.get('instructions', '')
            }
            order_item_pizza = OrderItemPizza.objects.create(**pizza_data_clean)

            # Create toppings
            for topping_data in toppings_data:
                topping = topping_data['topping']
                topping_data_clean = {
                    'order_item_pizza': order_item_pizza,
                    'topping': topping,
                    'portion': topping_data.get('portion', 'Normal'),
                    'side': topping_data.get('side', 'Whole')
                }
                OrderItemPizzaTopping.objects.create(**topping_data_clean)

        return order_item


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    delivery_address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), allow_null=True,
                                                          required=False)
    coupon = serializers.PrimaryKeyRelatedField(queryset=Coupon.objects.all(), allow_null=True, required=False)
    driver = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), allow_null=True, required=False)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'order_datetime', 'status', 'delivery_address', 'coupon',
            'total_amount', 'discount_amount', 'tax_amount', 'netto_total',
            'items', 'driver', 'estimated_delivery_time'
        ]
        read_only_fields = ['total_amount', 'discount_amount', 'tax_amount', 'netto_total', 'id']

    def create(self, validated_data):
        # Remove 'id' if present
        validated_data.pop('id', None)

        items_data = validated_data.pop('items')
        order = Order.objects.create(
            **validated_data,
            total_amount=0.0,
            discount_amount=0.0,
            tax_amount=0.0,
            netto_total=0.0
        )
        total_amount = Decimal(0.0)

        for item_data in items_data:
            # Convert model instances to IDs if necessary
            if isinstance(item_data.get('menu_item'), MenuItem):
                item_data['menu_item'] = item_data['menu_item'].id

            # Handle pizza data if present
            pizza_data = item_data.get('pizza', None)
            if pizza_data:
                if isinstance(pizza_data.get('size'), PizzaSize):
                    pizza_data['size'] = pizza_data['size'].id
                if isinstance(pizza_data.get('crust_type'), CrustType):
                    pizza_data['crust_type'] = pizza_data['crust_type'].id
                if isinstance(pizza_data.get('sauce'), Sauce):
                    pizza_data['sauce'] = pizza_data['sauce'].id
                if isinstance(pizza_data.get('cheese'), Cheese):
                    pizza_data['cheese'] = pizza_data['cheese'].id

                # Convert topping instances to primary key values
                toppings_data = pizza_data.get('toppings', [])
                for topping_data in toppings_data:
                    if isinstance(topping_data.get('topping'), Topping):
                        topping_data['topping'] = topping_data['topping'].id

            # Pass the order instance to the context of the OrderItemSerializer
            order_item_serializer = OrderItemSerializer(data=item_data, context={'order': order})
            order_item_serializer.is_valid(raise_exception=True)
            order_item = order_item_serializer.save()
            total_amount += order_item.total_price

        # Apply coupon if available
        discount_amount = Decimal(0.0)
        if order.coupon and order.coupon.is_valid():
            discount_amount = order.coupon.apply_discount(total_amount)

        # Calculate tax and netto total
        netto_total, tax_amount = calculate_net_and_tax(total_amount - discount_amount, tax_rate=0.08)

        # Update the order with calculated amounts
        order.total_amount = total_amount
        order.discount_amount = discount_amount
        order.tax_amount = tax_amount
        order.netto_total = netto_total
        order.save()

        return order
