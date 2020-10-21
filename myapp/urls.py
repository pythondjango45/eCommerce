from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('contact/',views.contact,name='contact'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('logout/',views.logout,name='logout'),
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('new_password/',views.new_password,name='new_password'),
    path('change_password/',views.change_password,name='change_password'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('activate_status/',views.activate_status,name='activate_status'),
    path('enter_email/',views.enter_email,name='enter_email'),
    path('add_product/',views.add_product,name='add_product'),
    path('view_product/',views.view_product,name='view_product'),
    path('product_detail/<int:pk>/',views.product_detail,name='product_detail'),
    path('product_unavailable/<int:pk>/',views.product_unavailable,name='product_unavailable'),
    path('get_unavailable/',views.get_unavailable,name='get_unavailable'),
    path('edit_product/<int:pk>/',views.edit_product,name='edit_product'),
    path('fashion/',views.fashion,name='fashion'),
    path('electronic/',views.electronic,name='electronic'),
    path('mobile/',views.mobile,name='mobile'),
    path('user_product_detail/<int:pk>/',views.user_product_detail,name='user_product_detail'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('mywishlist/',views.mywishlist,name='mywishlist'),
    path('remove_from_wishlist/<int:pk>/',views.remove_from_wishlist,name='remove_from_wishlist'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('mycart/',views.mycart,name='mycart'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('pay/',views.initiate_payment,name='pay'),
    path('callback/',views.callback,name='callback'),
    path('validate_username/',views.validate_username,name='validate_username'),
]
