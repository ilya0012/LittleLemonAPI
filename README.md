# LittleLemonAPI
Work with serializers, views and REST Framework

http://127.0.0.1:8000/api

# POST /api/users (No role required): Creates a new user with name, email, and password #
# GET /api/users/users/me/ (Authenticated user): Displays only the current user
# POST /token/login/ (Anyone with valid credentials): Generates access tokens for API authentication
# GET /api/menu-items (Customer, delivery crew): Lists all menu items
# GET /api/menu-items/{menuItem} (Customer, delivery crew): Lists a single menu item
# GET /api/groups/manager/users (Manager): Returns all managers
# POST /api/groups/manager/users (Manager): Assigns a user to the manager group
# DELETE /api/groups/manager/users/{userId} (Manager): Removes a user from the manager group
# GET /api/groups/delivery-crew/users (Manager): Returns all delivery crew
# POST /api/groups/delivery-crew/users (Manager): Assigns a user to the delivery crew group
# DELETE /api/groups/delivery-crew/users/{userId} (Manager): Removes a user from the delivery crew group
# GET /api/cart/menu-items (Customer): Returns current items in the cart
# POST /api/cart/menu-items (Customer): Adds a menu item to the cart
# DELETE /api/cart/menu-items (Customer): Deletes all menu items from the cart
# GET /api/orders (Customer, Manager): Returns orders with order items based on user role
# POST /api/orders (Customer): Creates a new order from the cart items
# GET /api/orders/{orderId} (Customer, Manager): Returns order details for a specific order
# PUT/PATCH /api/orders/{orderId} (Customer, Manager): Updates an order
# DELETE /api/orders/{orderId} (Manager): Deletes an order
# GET /api/orders (Delivery crew): Returns orders assigned to the delivery crew
# PATCH /api/orders/{orderId} (Delivery crew): Updates the status of an order assigned to the delivery crew
# 
Also added searching, pagination and filtering api/menu-items
