from rest_framework import serializers
from.models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class MenuItem_Serializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','title', 'price', 'featured', 'category']

class User_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','groups']

class Cart_Serializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']    
        
class AddtoCart_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']  
        
class Order_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user', 'delivery_crew', 'status', 'total', 'date']     
        
class Order_Item_Serializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']     