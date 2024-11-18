# Generated by Django 5.1.3 on 2024-11-17 14:57

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Driver",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("phone_number", models.CharField(max_length=20)),
                ("vehicle_info", models.CharField(max_length=255)),
                ("license_number", models.CharField(max_length=50)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
