from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from POS_system import views
from POS_system.forms import CustomAuthenticationForm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('POS_system.urls')),
    path('login/', 
         views.CustomLoginView.as_view(
             template_name='Authentication/login.html',
             authentication_form=CustomAuthenticationForm
         ), 
         name='login'),
         
    path('logout/', views.custom_logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('cashier-dashboard/', views.dashboard, name='cashier_dashboard'),
    path('register/', views.register_user, name='register_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/',views.delete_user, name='delete_user'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('products/', views.product_list, name='product_list'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('categories/', views.category_list, name='category_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('cart/', views.cart, name='cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
     path('cart/item/delete/<int:item_id>/', views.delete_cart_item, name='delete_cart_item'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('order_history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    #REPORTS AND SALES 
    path('sales_summary/', views.sales_report, name='sales_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('export_sales_report/', views.export_sales_report, name='export_sales_report'),
]
