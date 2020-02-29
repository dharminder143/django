from django.urls import path
from django.conf.urls import url
from . import views



urlpatterns = [
     path('', views.product, name='product'),
     path('signup/', views.signup, name='signup'),
     url(r'^activate/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
     path('product_detail/<int:pk>', views.product_detail, name='product_detail'),
     path('price/', views.price_greater, name='price_greater'),
     path('add_to_cart/<int:pk>', views.add_to_cart, name='add_to_cart'),
     path('post_new/', views.post_new, name='post_new'),
     path('product_list/', views.product_list, name='product_list'),
     path('product_edit/<int:pk>', views.product_edit, name='product_edit'),
     path('post_remove/<int:pk>', views.post_remove, name='post_remove'),
     path('published/<int:pk>', views.published_views, name='published'),
     path('cart/', views.Cart_view, name='cart'),
     path('decreaseCart/<int:pk>', views.decreaseCart, name='decreaseCart'),
     path('payment/', views.payment, name="payment"),
     path('charge/', views.charge, name="charge"),

     path('checkout/', views.checkout, name='checkout'),
     path('delete_cart/<int:pk>', views.delete_cart, name='delete_cart'),
     path('search/', views.search, name='search'),  
     path('profile_list/', views.profile_list, name='profile_list'),
     path('wish_list/<int:pk>', views.add_to_wishlist, name='wish_list'),
     path('contact/',views.contact, name='contact'),
     path('order_view/',views.order_view, name='order_view'),
     path('wish_list/',views.wish_list,name='wish_list'),
     path('remove_wish/<int:pk>',views.remove_wish,name='remove_wish'),
     path('wish1_add_to_card/<int:pk>',views.wish1_add_to_card,name='wish1_add_to_card'),
     path('add_all_pro',views.add_all_pro,name='add_all_pro'),
     path('order_cat/<int:pk>',views.order_cat,name='order_cat'),
     path('weekly/',views.weekly,name='weekly')

     






]