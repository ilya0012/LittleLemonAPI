from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token 

urlpatterns = [
   path('category', views.CategoryView.as_view()),
   path('menu-items', views.menu_items),
   path('menu-items/<int:pk>', views.SingleItemView.as_view()),
   path('groups/manager/users', views.managers_group),
   path('groups/manager/users/<int:id>', views.delete_manager),
   path('groups/delivery-crew/users',views.deliveryCrew_groupView),
   path('groups/delivery-crew/users/<int:id>',views.delete_deliveryCrew),
   path('cart/menu-items', views.CartMenuItemView.as_view()),
   path('orders', views.place_orderView),
   path('orders/<int:pk>', views.SingleOrderItemView.as_view()),
]
