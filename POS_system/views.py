from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.contrib.auth import login,update_session_auth_hash,logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse
from django.db.models import Sum
from collections import defaultdict
from django.urls import reverse
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect

@login_required
def register_device(request):
    ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')

    # Create or update the device record
    Device.objects.update_or_create(
        user=request.user,
        ip_address=ip,
        user_agent=user_agent
    )

    return HttpResponseRedirect('/') 

def device_list(request):
    devices = Device.objects.filter(user=request.user)
    return render(request, 'device_list.html', {'devices': devices})



@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

def home(request):
    posts_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts_list, 5)  # 5 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    return render(request, 'home.html', {'posts': posts})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account Created! Ask Admin to Activate')  
            return redirect('login')
        else:
            # If the form is not valid, display an error message.
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm() 

    return render(request, 'Authentication/signup.html', {'form': form})


class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)  # Log the user in
        
        # Register the device
        self.register_device(user)

        if user.is_staff: 
            messages.success(self.request, 'Log In Successful!')
            return redirect(reverse('admin_dashboard'))  # Redirect to admin dashboard
        else:
            messages.success(self.request, 'Log In Successful!')
            return redirect(reverse('cashier_dashboard'))

    def register_device(self, user):
        ip = self.request.META.get('REMOTE_ADDR')
        user_agent = self.request.META.get('HTTP_USER_AGENT')

        # Create or update the device record
        Device.objects.update_or_create(
            user=user,
            ip_address=ip,
            user_agent=user_agent
        )
        
def custom_logout_view(request):
    logout(request) 
    messages.success(request, 'You have been logged out successfully.')  
    return redirect('login')

# Check if user is an admin
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def register_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')  

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register_user')

        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, user_type='cashier')  
        messages.success(request, "User registered successfully.")
        return redirect('admin_dashboard')  
    return render(request, 'Authentication/register_user.html')

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Set the timezone to Asia/Manila
    manila_timezone = timezone.get_current_timezone()
    today = timezone.now().astimezone(manila_timezone).date()

    # Get today's orders and recent transactions (limit to last 10)
    orders = Order.objects.filter(created_at__date=today)
    recent_orders = Order.objects.order_by('-created_at')[:10]
    top_products = defaultdict(int)
    # Aggregate sales data for the chart
    sales_data = defaultdict(int)
    for order in orders:
        for item in order.items.all():  # Ensure 'Order' uses related_name='items'
            sales_data[item.product.name] += item.quantity
            top_products[item.product.name] += item.quantity 
    

    # Prepare data for Chart.js
    labels = list(sales_data.keys())  # Product names
    quantities = list(sales_data.values())  # Corresponding quantities sold
    sorted_top_products = sorted(top_products.items(), key=lambda x: x[1], reverse=True)[:5]

    # Calculate total sales
    total_sales = sum(order.total_price for order in orders)
    total_sales_today = sum(order.total_price for order in Order.objects.filter(created_at__date=today))
    total_transactions = Order.objects.filter(created_at__date=today).count()
    average_sale_value = total_sales_today / total_transactions if total_transactions > 0 else 0
    total_orders_today = Order.objects.filter(created_at__date=today).count()
    

    low_stock_threshold = 5  # Define your threshold for low stock
    low_stock_products = Product.objects.filter(stock__lt=low_stock_threshold)



    context = {
        'labels': labels,
        'quantities': quantities,
        'total_sales': total_sales,
        'total_orders_today': total_orders_today,
        'recent_orders': recent_orders, 
        'top_products': sorted_top_products, 
        'low_stock_products': low_stock_products,
        'total_sales_today': total_sales_today,
        'total_transactions': total_transactions,
        'average_sale_value': average_sale_value,
    }
    return render(request, 'Admin/dashboard.html', context)

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')  # Get new password from the form
        user_type = request.POST.get('user_type')

        user.username = username

        # Update password only if a new one is provided
        if password:  # Check if a new password was given
            user.password = (password)  
        user.userprofile.user_type = user_type
        user.save()
        user.userprofile.save()

        messages.success(request, "User updated successfully.")
        return redirect('admin_dashboard')

    return render(request, 'admin/edit_user.html', {'user': user})

@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')

@login_required
def update_profile(request):
    if request.method == "POST":
        user = request.user
        new_password = request.POST.get('new_password')
        
        if new_password:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  
            messages.success(request, "Your password has been updated successfully.")
            return redirect('admin_dashboard') 
        messages.warning(request, "Please enter a new password.")
        return redirect('update_profile')

    return render(request, 'Authentication/profile.html')

@login_required
def dashboard(request):

    return render(request, 'dashboard.html')


@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # For cart
    cart_items = CartItem.objects.filter(user=request.user, order__isnull=True)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Handling Product and Category Form submissions
    if request.method == "POST":
        if 'add_product' in request.POST:  # Check if the product form is submitted
            product_form = ProductForm(request.POST)
            if product_form.is_valid():
                product_form.save()
                messages.success(request, "Product added successfully.")
                return redirect('product_list')
        elif 'add_category' in request.POST:  # Check if the category form is submitted
            category_form = CategoryForm(request.POST)
            if category_form.is_valid():
                category_form.save()
                messages.success(request, "Category added successfully.")
                return redirect('product_list')
        
        elif 'edit_category' in request.POST:  # Check if the category edit form is submitted
            category_id = request.POST.get('category_id')
            category_name = request.POST.get('category_name')

            # Get the category or return a 404 if not found
            category = get_object_or_404(Category, id=category_id)
            category.name = category_name  # Update the category name
            category.save()  # Save the updated category
            messages.success(request, "Category updated successfully.")
            return redirect('product_list')

    # If there was no POST, we want to create empty forms
    product_form = ProductForm()  
    category_form = CategoryForm()

    context = {
        'products': products,
        'product_form': product_form,  
        'category_form': category_form,  
        'categories': categories,
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'Product/product_list.html', context)

@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'Product/add_product.html', {'form': form})

@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'Product/edit_product.html', {'form': form, 'product': product})

@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('product_list')
    return render(request, 'admin/delete_product.html', {'product': product})

def category_list(request):
    categories = Category.objects.all()
    messages.success(request, "Product added successfully.")
    return render(request, 'Product/category_list.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
        else:
            return redirect('product_list')
    else:
        form = CategoryForm()
    return render(request, 'Product/add_category.html', {'form': form})

@user_passes_test(is_admin)
def edit_category(request, category_id):
    # Fetch the category or return 404 if not found
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category_name = request.POST.get("category_name")
        
        # Validate the category name if necessary (optional)
        if category_name:
            category.name = category_name  # Update the category name
            category.save()  # Save the updated category
            messages.success(request, "Category updated successfully.")
            return redirect('product_list')  # Redirect to the product list after editing

    # If it's a GET request or if there's an error in the POST, render the edit form
    context = {
        'category': category,
    }
    return render(request, 'path/to/edit_category_template.html', context)

@login_required
def delete_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user, order__isnull=True)
    cart_item.delete()  
    messages.success(request, "Item removed from the cart.")
    return redirect('product_list')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user, order__isnull=True) 
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'Cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})
@login_required
def update_cart_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user, order__isnull=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added one more {cart_item.product.name}.")
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, f"Removed one {cart_item.product.name}.")
            else:
                cart_item.delete()
                messages.success(request, f"{cart_item.product.name} removed from cart.")

    return redirect('product_list')
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(
        product=product, user=request.user, order__isnull=True
    )
    
    if not created:
        cart_item.quantity += 1  # Increment quantity if it already exists
    cart_item.save()

    messages.success(request, f"{product.name} added to cart.")

    # Redirect with a flag to trigger the cart modal
    return redirect(f"{request.META.get('HTTP_REFERER')}?open_cart=true")

@login_required
def checkout(request):
    # Fetch the cart items for the current user that have not been assigned to an order
    cart_items = CartItem.objects.filter(user=request.user, order__isnull=True)

    if not cart_items:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('cart')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # Create a new order for the user
    order = Order.objects.create(user=request.user, total_price=total_price)

    # Prepare the order summary
    order_summary = []
    for item in cart_items:
        item.order = order  # Assign the cart item to the new order
        item.product.stock -= item.quantity  # Reduce product stock
        item.product.save()  # Save the product with updated stock
        item.save()  # Save the cart item with the assigned order

        # Append to order summary (item name, quantity, total price)
        order_summary.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'total': item.product.price * item.quantity,
        })

    # Clear the cart after successful checkout
    cart_items.delete()  # This will remove all items from the cart

    messages.success(request, "Your order, Checkout successful!")

    # Render the checkout success page or redirect to a success URL
    return render(request, 'Cart/checkout_success.html', {'order': order, 'order_summary': order_summary, 'total_price': total_price})

@login_required
def order_history(request):
    # Fetch all orders associated with the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Order/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()  # Fetch items related to this order
    return render(request, 'Order/order_detail.html', {'order': order, 'order_items': order_items})


#SALES & INVENTORY REPORTS

@login_required
@user_passes_test(is_admin)
def sales_report(request):
    # Handle GET or POST request
    if request.method == 'POST':
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
    else:  # Handle GET request
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

    # Initialize orders and sales data
    orders = Order.objects.none()
    sales_data = defaultdict(lambda: defaultdict(int))

    if start_date_str and end_date_str:
        # Convert date strings to timezone-aware datetime objects
        start_date = timezone.make_aware(timezone.datetime.strptime(start_date_str, "%Y-%m-%d"))
        end_date = timezone.make_aware(timezone.datetime.strptime(end_date_str, "%Y-%m-%d")) + timedelta(hours=23, minutes=59, seconds=59)

        # Filter orders based on the date range
        orders = Order.objects.filter(created_at__range=[start_date, end_date])

        # Aggregate sales data for the chart
        for order in orders:
            for item in order.items.all():  # Use `related_name='items'` from the Order model
                sales_data[order.created_at.date()][item.product.name] += item.quantity

    # Prepare data for Chart.js
    labels = sorted(sales_data.keys())
    products = sorted(set(product for date in sales_data for product in sales_data[date]))
    dataset = {product: [sales_data[date][product] for date in labels] for product in products}

    # Calculate total sales
    total_sales = sum(order.total_price for order in orders)
    labels = [date.strftime("%Y-%m-%d") for date in sorted(sales_data.keys())]
    # Render the template with the context
    return render(request, 'Sales&InventoryReport/sales_report.html', {
        'orders': orders,
        'total_sales': total_sales,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'labels': labels,
        'products': products,
        'dataset': dataset,
    })

@login_required
@user_passes_test(is_admin)
def export_sales_report(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Initialize orders as an empty queryset
    orders = Order.objects.none()

    if start_date_str and end_date_str:
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date) + timedelta(hours=23, minutes=59, seconds=59)
        orders = Order.objects.filter(created_at__range=[start_date, end_date])

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)

    # Write the CSV header
    writer.writerow(['Order ID', 'Username', 'Total Price ($)', 'Created At', 'Item Count'])

    # Write data rows
    for order in orders:
        writer.writerow([
            order.id,
            order.user.username,
            f"{order.total_price:.2f}",  # Format price to two decimal places
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Format datetime
            order.items.count()  # Assuming Order has a related name 'items' for count of order items
        ])

    return response
@login_required
@user_passes_test(is_admin)
def inventory_report(request):
    products = Product.objects.all()  # Fetch all products
    low_stock = products.filter(stock__lt=5)  # Example threshold for low stock

    return render(request, 'Sales&InventoryReport/inventory_report.html', {
        'products': products,
        'low_stock': low_stock
    })

def cashier_dashboard(request):
    return render(request, 'dashboard.html') 