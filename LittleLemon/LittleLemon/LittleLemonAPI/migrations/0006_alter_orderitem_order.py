# Generated by Django 4.2.2 on 2023-06-22 20:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0005_alter_menuitem_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="LittleLemonAPI.order"
            ),
        ),
    ]
