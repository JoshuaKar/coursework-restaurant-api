from django.shortcuts import render
from.models import MenuItem, Cart, Order, OrderItem
#from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import permission_classes, api_view, throttle_classes
from rest_framework import status
from .serializers import MenuItem_Serializer, User_Serializer, Cart_Serializer, AddtoCart_Serializer, Order_Serializer, Order_Item_Serializer
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import AnonRateThrottle


@api_view(['GET','POST'])
@throttle_classes([AnonRateThrottle])#Only throttled for Anon Users
@permission_classes([IsAuthenticatedOrReadOnly])#All users must be authenticated to access
def menuitem(request):
    #All users can access the GET method
    if request.method=='GET':                    
        queryset = MenuItem.objects.all()
        ###    
        category_name = request.query_params.get('category')
        price = request.query_params.get('price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        #Queries
        if category_name:
            queryset = queryset.filter(category__title=category_name)
        if price:
            queryset = queryset.filter(price__lte=price)
        if search:
            queryset = queryset.filter(title__startswith=search)
        if ordering:
            ordering_fields = ordering.split(",")
            queryset = queryset.order_by(*ordering_fields)
        #Paginator
        paginator = Paginator(queryset, per_page=perpage)
        try:
            queryset = paginator.page(number=page)
        except EmptyPage:
            queryset = []    
            
        serializer = MenuItem_Serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        ###

    #Only Managers can access the POST, PUT, PATCH, DELETE methods
    if request.user.groups.filter(name='manager').exists():       
        if request.method=='POST':
            serializer = MenuItem_Serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
    
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
            
@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])#All users must be authenticated to access
def single_menuitem(request, pk):   
    single_item = MenuItem.objects.get(pk=pk)
    if request.method=='GET':                           
        serializer = MenuItem_Serializer(single_item)
        return Response(serializer.data)
    
    if request.user.groups.filter(name='manager').exists():  
        if request.method=='PUT':
            serializer = MenuItem_Serializer(single_item, data=request.data)
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        if request.method=='PATCH':
            serializer = MenuItem_Serializer(single_item, data=request.data, partial=True)
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        if request.method=='DELETE':
            single_item.delete()
            return Response(status=status.HTTP_200_OK)
            
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def groups_view(request, group):
    if request.user.groups.filter(name='manager').exists(): 
                
        if request.method=='GET':
            if group == 'manager':
                serializer = User_Serializer(User.objects.filter(groups__name='manager'), many=True)
                return Response(serializer.data)
            if group == 'delivery-crew':
                serializer = User_Serializer(User.objects.filter(groups__name='delivery-crew'), many=True)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if request.method=='POST':
            if group == 'manager':
                serializer = User_Serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
            if group == 'delivery-crew':
                serializer = User_Serializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user_group_view(request, group, pk):
    #Will crash if cant find user same with above delete 
    single_user = User.objects.get(pk=pk)
    if request.method=='DELETE':
        groups = Group.objects.get(name=group)
        groups.user_set.remove(single_user)
        return Response(status=status.HTTP_200_OK)
      
@api_view(['GET','POST','DELETE'])
#no permissions needed since cart can be accessed by all customers
def cart_view(request):
    if request.method=='GET':
        serialized = Cart_Serializer(Cart.objects.filter(user=request.user), many=True)
        return Response(serialized.data)
    if request.method=='POST': 
        new_item = AddtoCart_Serializer(data=request.data)
        if new_item.is_valid():
            menuitem_id = new_item.validated_data['menuitem'].id
            menuitem = MenuItem.objects.get(id=menuitem_id)
            quantity = new_item.validated_data['quantity']
            user_id = request.user.id 
                       
            cart, created = Cart.objects.update_or_create(
                menuitem=menuitem,
                user_id=user_id,
                defaults={
                    'quantity': quantity,
                    'unit_price': menuitem.price,
                    'price': menuitem.price * quantity
                }
            )
            if created:
                serializer = Cart_Serializer(cart)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(new_item.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method=='DELETE':
        serialized = Cart.objects.filter(user=request.user)
        serialized.delete()
        return Response(status=status.HTTP_200_OK)
            
@api_view(['GET','POST'])
@permission_classes([IsAuthenticatedOrReadOnly])  
def orders_view(request):     
    if request.method=='GET':
        if request.user.groups.filter(name='manager').exists():
            queryset = Order.objects.all()
        elif request.user.groups.filter(name='delivery-crew').exists():
            queryset = Order.objects.filter(delivery_crew=request.user)
        else:
            queryset = Order.objects.filter(user=request.user)
        ###    
        delivery_crew = request.query_params.get('delivery_crew')
        delivery_status = request.query_params.get('status')
        #search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        #Queries
        if delivery_crew:
            queryset = queryset.filter(delivery_crew=delivery_crew)
        if delivery_status:
            queryset = queryset.filter(status=delivery_status)
        #if search:
        #    queryset = queryset.filter(title__startswith=search)
        if ordering:
            ordering_fields = ordering.split(",")
            queryset = queryset.order_by(*ordering_fields)
        #Paginator
        paginator = Paginator(queryset, per_page=perpage)
        try:
            queryset = paginator.page(number=page)
        except EmptyPage:
            queryset = []    
            
        serializer = Order_Serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        ###
        
    if request.method=='POST':
        
        cart = Cart.objects.filter(user=request.user)  
        subtotal = 0.00
        if cart.exists():
            order = Order.objects.create(user=request.user, total=0.00)          
            for cart_item in cart:
                order_item = OrderItem.objects.create(
                    order = order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price
                )
                subtotal+=float(cart_item.price)
                order_item.save()   
                                   
            order.delivery_crew=User.objects.get(username='deliverycrew')
            order.status=False
            order.total=subtotal
            order.save()
            #DELETE CART#
            #############
            cart.delete()
            return Response(Order_Serializer(order).data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Error: Empty Cart!"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])#All users must be authenticated to access
def order_specifics(request, pk):
    if request.method == 'GET':
        queryset = Order_Item_Serializer(OrderItem.objects.filter(order_id=pk), many=True)
        return Response(queryset.data, status=status.HTTP_200_OK)