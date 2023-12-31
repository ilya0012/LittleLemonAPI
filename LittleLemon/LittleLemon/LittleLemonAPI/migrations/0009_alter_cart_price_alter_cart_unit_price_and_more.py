# Generated by Django 4.2.2 on 2023-06-24 16:43

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0008_alter_cart_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cart",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AlterField(
            model_name="cart",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AlterField(
            model_name="order",
            name="date",
            field=models.DateField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
