from django.shortcuts import get_object_or_404
from .serializers import CategorySerializer, CartSerializer, OrderSerializer, MenuItemsSerializer, OrderItemSerializer
from .models import Category, Cart, Order, OrderItem, MenuItem
from rest_framework import generics, status
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from django.contrib.auth.models import User, Group
from django.utils import timezone
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.paginator import Paginator, EmptyPage

# additional perrmission class to check manager
class IsManager(BasePermission):
    def has_permission(self, request, view):
        # Check if the user belongs to the 'Manager' group
        return request.user.groups.filter(name='Manager').exists()
    
# additional permission class to check delivery_crew
class IsDelivery(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='delivery_crew').exists()

# simple watch id categories /api/categories
class CategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# /api/menu-items
@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def menu_items(request):
    denied_request = Response('access denied, not authorized user',status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        perpage = request.query_params.get('perpage', default=3)
        page = request.query_params.get('page', default=1)
        items = MenuItem.objects.select_related('category').all()

        search = request.query_params.get('search')
        to_price = request.query_params.get('to_price')
        if to_price:
            items = items.filter(price=to_price)
        if search:
            items = items.filter(title__istartswith=search)

        ordering = request.query_params.get('ordering')
        if ordering:
            items = items.order_by(ordering)
 
        paginator = Paginator(items, per_page=perpage)        
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []

        serialized_item = MenuItemsSerializer(items, many=True)       
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    if request.method == 'POST':
        if not request.user.groups.filter(name='Manager').exists():
            return denied_request
        else:
            serialized_item = MenuItemsSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
        
    if request.method == 'PUT' or 'PATCH' or 'DELETE':
        if not request.user.groups.filter(name='Manager').exists():
            return denied_request
        else:
            return Response('Go to /menu-items/<int:id> to use this function', status.HTTP_405_METHOD_NOT_ALLOWED)

    
# /api/menu-items/{MenuItem}    
class SingleItemView(generics.DestroyAPIView, generics.RetrieveAPIView, generics.UpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    permission_classes = [IsManager]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method != 'GET':
            permission_classes = [IsManager]
        else:
            permission_classes = []
        
        return [permission() for permission in permission_classes]
    

# /api/groups/manager/users
@api_view(['POST', 'GET'])
@permission_classes([IsManager, IsAdminUser ])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def managers_group(request):
    managers = Group.objects.get(name='Manager')

    if request.method == 'GET':    
        users = managers.user_set.all()
        user_data = [
            {
                'id': user.id,
                'username': user.username,
            }
            for user in users   
        ]
        return Response({"users": user_data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers.user_set.add(user)
            return Response({"message": "Manager Authorized, user added"}, status.HTTP_201_CREATED)
        

# /api/groups/manager/users/{userId}
@api_view(['DELETE'])
@permission_classes([IsManager])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def delete_manager(request, id):
    user = get_object_or_404(User, id=id)
    managers_group = Group.objects.get(name='Manager')
    managers_group.user_set.remove(user)
    return Response({"message": "User removed from Manager group"}, status=status.HTTP_200_OK)
        

# /api/groups/delivery-crew/users
@api_view(['POST', 'GET'])
@permission_classes([IsManager])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def deliveryCrew_groupView(request):
    managers = Group.objects.get(name='delivery_crew')

    if request.method == 'GET':    
        users = managers.user_set.all()
        user_data = [
            {
                'id': user.id,
                'username': user.username
            }
            for user in users
        ]
        return Response({"users": user_data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers.user_set.add(user)
            return Response({"message": "Manager Authorized, user added"}, status.HTTP_201_CREATED)
        

# /api/groups/delivery-crew/users/{userId}
@api_view(['DELETE'])
@permission_classes([IsManager])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def delete_deliveryCrew(request, id):
    user = get_object_or_404(User, id=id)
    managers_group = Group.objects.get(name='delivery_crew')
    managers_group.user_set.remove(user)
    return Response({"message": "User removed from Manager group"}, status=status.HTTP_200_OK)

# /api/cart/menu-items
class CartMenuItemView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_queryset(self):
        user = self.request.user
        queryset = Cart.objects.all().filter(user = user)
        return queryset

    def perform_create(self, serializer):     
        serializer.save(user=self.request.user)
        
    def delete(self, request):
        cart = Cart.objects.all()
        cart.delete()
        return Response({'message': 'all items deleted'}, status.HTTP_200_OK)
    

# /api/orders
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def place_orderView(request):
    if request.method == 'GET':    
        if request.user.groups.filter(name='Manager').exists():
            orders = OrderItem.objects.all()
            serialized_item = OrderItemSerializer(orders, many=True)
            return Response(serialized_item.data, status.HTTP_200_OK)   
        
        if request.user.groups.filter(name='delivery_crew').exists():
            user = request.user
            orders = OrderItem.objects.filter(order__delivery_crew=user)
            serialized_item = OrderItemSerializer(orders, many=True)
            return Response(serialized_item.data, status.HTTP_200_OK)
        
        else:
            user = request.user
            orders = OrderItem.objects.filter(order__user=user)
            serialized_item = OrderItemSerializer(orders, many=True)
            return Response(serialized_item.data, status.HTTP_200_OK)

    if request.method == 'POST':
        if not request.user.groups.filter(name='delivery_crew').exists() and not request.user.groups.filter(name='Manager').exists():
            user = request.user

            # Retrieve the current user's cart items
            cart_items = Cart.objects.filter(user=user)

            if not cart_items.exists():
                return Response({'message': 'Cart is empty'}, status.HTTP_400_BAD_REQUEST)

            # Create a new order
            order = Order.objects.create(user=user, total=0, date=timezone.now())

            # Create order items from cart items
            order_items = []
            for cart_item in cart_items:
                menuitem = cart_item.menuitem
                quantity = cart_item.quantity

                # Create an order item
                order_item = OrderItem.objects.create(
                    order=order,
                    menuitem=menuitem,
                    quantity=quantity,
                    unit_price=menuitem.price,
                    price=menuitem.price * quantity
                )
                order_items.append(order_item)

            # Calculate the total price of the order
            total_price = sum(order_item.price for order_item in order_items)

            # Update the total price of the order
            order.total = total_price
            order.save()

            # Delete cart items
            cart_items.delete()

            # Serialize the created order items
            serialized_items = OrderItemSerializer(order_items, many=True)

            return Response(serialized_items.data, status.HTTP_201_CREATED)
         
        else:
            return Response({'mesage': 'You are not allowed to do it'}, status.HTTP_401_UNAUTHORIZED)


# /api/orders/{orderId}
class SingleOrderItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = []
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method == 'GET':
            if self.request.user.groups.filter(name='delivery_crew').exists():
                self.permission_classes = [IsAuthenticated]
        elif self.request.method in ['PATCH', 'PUT']:
            if self.request.user.groups.filter(name='delivery_crew').exists():
                self.permission_classes = [IsAuthenticated]
            elif self.request.user.groups.filter(name='Manager').exists():
                self.permission_classes = [IsManager]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        order = self.get_object()

        if (
            not request.user.groups.filter(name='delivery_crew').exists()
            and not request.user.groups.filter(name='Manager').exists()
            and order.user != request.user
        ):
            return Response(
                {'error': 'You do not have permission to access this order.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serialized_order = self.serializer_class(order)
        serialized_order_data = serialized_order.data

        order_items = OrderItem.objects.filter(order=order).values(
            'id', 'menuitem', 'menuitem__title', 'quantity', 'unit_price', 'price', 'order__user__username'
        )
        serialized_order_data['order_items'] = order_items

        return Response(serialized_order_data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Check if the user is a manager
        is_manager = request.user.groups.filter(name='Manager').exists()

        # Check if the delivery_crew field is being updated
        if 'delivery_crew' in request.data:
            # Check if the authenticated user is a manager
            if not is_manager:
                return Response(
                    {'error': 'You do not have permission to assign a delivery crew.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if the assigned delivery_crew is part of the "delivery_crew" group
            delivery_crew_id = request.data.get('delivery_crew')
            delivery_crew_exists = User.objects.filter(
                id=delivery_crew_id, groups__name='delivery_crew'
            ).exists()
            if not delivery_crew_exists:
                return Response(
                    {
                        'error': 'Invalid delivery crew. Please select a valid delivery crew '
                                 'from the "delivery_crew" group.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Exclude the 'user' field from the update process during PUT
        request_data = request.data.copy()
        request_data.pop('user', None)

        serialized_order = self.serializer_class(order, data=request_data, partial=True)
        if serialized_order.is_valid():
            serialized_order.save()
            return Response(serialized_order.data, status=status.HTTP_200_OK)

        return Response(serialized_order.errors, status=status.HTTP_400_BAD_REQUEST)
    
