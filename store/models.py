from uuid import uuid4
from django.core.validators import MinValueValidator
from django.db import models

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


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null = True)
    membership = models.CharField(
        max_length = 1,
        choices = MEMBERSHIP_CHOICES,
        default = 'B'
        )
    def __str__(self):
        return self.first_name + " " + self.last_name

class Order(models.Model):
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
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orderitems")
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
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