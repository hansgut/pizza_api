# Generated by Django 5.1.3 on 2024-11-18 18:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_alter_order_discount_amount_alter_order_grand_total_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="grand_total",
            new_name="netto_total",
        ),
    ]