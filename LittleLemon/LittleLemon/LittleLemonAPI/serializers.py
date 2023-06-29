from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'featured', 'price', 'category', 'category_id']
        extra_kwargs = {
            'price': {"min_value": 5}
        }
       # category_id : 2 == food
       # category_id : 3 == instruments
       # category_id : 5 == books

class CartSerializer(serializers.ModelSerializer):
    username_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    menuitem_name = serializers.ReadOnlyField(source='menuitem.title')
    price = serializers.SerializerMethodField(read_only=True)
    unit_price = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Cart
        fields = ['username_id', 'username', 'menuitem', 'menuitem_name', 'unit_price', 'quantity', 'price']
    
    def get_price(self, obj):
        return obj.quantity * obj.unit_price

    def get_unit_price(self, obj):
        return obj.menuitem.price
    
    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * validated_data['quantity']
        return super().create(validated_data)
    
    
class OrderSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField(read_only=True)
    date = serializers.ReadOnlyField(read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    delivery_crew_username = serializers.ReadOnlyField(source='delivery_crew.username')
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'username', 'delivery_crew', 'delivery_crew_username', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem_name = serializers.ReadOnlyField(source='menuitem.title')
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    username = serializers.ReadOnlyField(source='order.user.username')
    order = OrderSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'menuitem_name', 'quantity', 'unit_price', 'price', 'username', 'order']
        