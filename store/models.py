from uuid import uuid4
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings
from django.contrib import admin

from store.validators import validate_file_size

# Create your models here.
class Collection(models.Model):
    title = models.CharField(max_length=255)
    # circular dependency
    # do not create the reverse relationship by setting related_name = "+"
    featured_product = models.ForeignKey(
        'Product',
        on_delete = models.SET_NULL,
        null = True,
        related_name="+"
    )

    def __str__(self) -> str:
        return self.title
    class Meta:
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=255)
    # slug is for search engine to find it easier
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    # decimalfield only accepts kwargs
    unit_price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )
    inventory = models.PositiveIntegerField()
    last_update = models.DateTimeField(auto_now=True)
    # do not delete product if we delete the collection
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT, related_name='products')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='store/images',
        validators=[validate_file_size]
        )

class Customer(models.Model):
    class Meta:
        ordering = ['user__first_name', 'user__last_name']
        permissions = [
            ('view_history', 'Can view history'),
        ]

    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]

    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null = True)
    membership = models.CharField(
        max_length = 1,
        choices = MEMBERSHIP_CHOICES,
        default = 'B'
        )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
    
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

class Order(models.Model):
    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]

    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1,
        choices = PAYMENT_STATUS_CHOICES,
        default='P'
    )
    # never delete orders, even the customer is deleted
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    class Meta:
        unique_together = [['cart', 'product']]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        )
    zipcode = models.CharField(max_length=255)

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)