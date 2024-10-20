from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=256)
    last_login = models.DateTimeField(auto_now=True)  
    def __str__(self):
        return f"{self.user.username}'s device ({self.ip_address})"

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('cashier', 'Cashier'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.user_type}"
    
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title
    
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Clothing', 'Clothing'),
        ('Accessories', 'Accessories'),
        ('Footwear', 'Footwear'),
        ('Beauty Products', 'Beauty Products'),
    ]
    
    name = models.CharField(
        max_length=100, 
        choices=CATEGORY_CHOICES, 
        unique=True
    )

    def __str__(self):
        return self.get_name_display() 
    
class Brand (models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(default=now)  # Use real-time when creating an order
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username if self.user else 'Guest'} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)  

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"