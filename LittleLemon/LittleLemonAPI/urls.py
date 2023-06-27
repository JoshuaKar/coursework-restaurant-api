from django.urls import path, include
from .views import menuitem, single_menuitem, groups_view, delete_user_group_view, cart_view, orders_view, order_specifics
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('menu-items/', menuitem),
    path('menu-items/<int:pk>/', single_menuitem),
    path('', include('djoser.urls')),
    path('groups/<str:group>/users/', groups_view),
    path('groups/<str:group>/users/<int:pk>/', delete_user_group_view),
    path('cart/menu-items/', cart_view),
    path('orders/', orders_view),
    path('orders/<int:pk>/', order_specifics),   
    path('api-token-auth/', obtain_auth_token),
]
