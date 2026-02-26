from django.urls import path
from . import views

urlpatterns = [
    path('',               views.home_view,         name='home'),
    path('menu/',          views.menu_view,          name='menu'),
    path('contact/',       views.contact_view,       name='contact'),
    path('login/',         views.login_view,         name='login'),
    path('register/',      views.register_view,      name='register'),
    path('logout/',        views.logout_view,        name='logout'),
    path('profile/',       views.profile_view,       name='profile'),
    path('admin-panel/',   views.admin_panel_view,   name='admin_panel'),
    path('cart/',                   views.cart_view,          name='cart'),
    path('cart/add/<int:pk>/',      views.add_to_cart,        name='add_to_cart'),
    path('cart/remove/<int:pk>/',   views.remove_from_cart,   name='remove_from_cart'),
    path('cart/update/<int:pk>/',   views.update_cart,        name='update_cart'),
    path('cart/checkout/',          views.checkout_view,      name='checkout'),
    path('orders/',                 views.orders_view,        name='orders'),
    path('orders/update-status/<int:pk>/', views.update_order_status, name='update_order_status'),
]
