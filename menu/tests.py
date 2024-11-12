from django.test import TestCase
from .models import Category, MenuItem, PizzaSize, CrustType, Sauce, Cheese, Topping


class CategoryModelTest(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Appetizers", description="Starters and snacks")
        self.assertEqual(str(category), "Appetizers")
        self.assertEqual(category.description, "Starters and snacks")


class MenuItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Main Course")

    def test_menu_item_creation(self):
        menu_item = MenuItem.objects.create(
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce and cheese",
            price=10.99,
            is_pizza=True,
            is_active=True,
            category=self.category,
        )
        self.assertEqual(str(menu_item), "Margherita Pizza")
        self.assertEqual(menu_item.price, 10.99)
        self.assertTrue(menu_item.is_pizza)
        self.assertEqual(menu_item.category, self.category)

    def test_menu_item_null_category(self):
        menu_item = MenuItem.objects.create(
            name="Garlic Bread",
            price=3.99,
            is_pizza=False,
            category=None,
        )
        self.assertIsNone(menu_item.category)


class PizzaSizeModelTest(TestCase):
    def test_pizza_size_creation(self):
        size = PizzaSize.objects.create(name="Medium", diameter=12.0, base_price=15.00)
        self.assertEqual(str(size), 'Medium (12.0" inches)')
        self.assertEqual(size.base_price, 15.00)


class CrustTypeModelTest(TestCase):
    def test_crust_type_creation(self):
        crust = CrustType.objects.create(name="Thin Crust", price=2.50)
        self.assertEqual(str(crust), "Thin Crust")
        self.assertEqual(crust.price, 2.50)


class SauceModelTest(TestCase):
    def test_sauce_creation(self):
        sauce = Sauce.objects.create(name="Tomato Sauce", price=1.00)
        self.assertEqual(str(sauce), "Tomato Sauce")
        self.assertEqual(sauce.price, 1.00)


class CheeseModelTest(TestCase):
    def test_cheese_creation(self):
        cheese = Cheese.objects.create(name="Mozzarella", price=2.00)
        self.assertEqual(str(cheese), "Mozzarella")
        self.assertEqual(cheese.price, 2.00)


class ToppingModelTest(TestCase):
    def test_topping_creation(self):
        topping = Topping.objects.create(
            name="Pepperoni",
            price=1.50,
            is_vegetarian=False,
            is_vegan=False,
            is_meat=True,
            is_active=True,
        )
        self.assertEqual(str(topping), "Pepperoni")
        self.assertTrue(topping.is_meat)
        self.assertFalse(topping.is_vegetarian)

    def test_topping_vegetarian(self):
        topping = Topping.objects.create(
            name="Mushrooms",
            price=1.25,
            is_vegetarian=True,
            is_vegan=True,
            is_meat=False,
        )
        self.assertTrue(topping.is_vegetarian)
        self.assertTrue(topping.is_vegan)

    def test_topping_deactivation(self):
        topping = Topping.objects.create(
            name="Anchovies",
            price=1.75,
            is_active=False,
        )
        self.assertFalse(topping.is_active)
