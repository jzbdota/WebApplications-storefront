from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from store.signals import order_created
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage, Review

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'unit_price'
        ]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def save(self, **kwargs):
        product_id = self.context['product_id']

        self.instance = ProductImage.objects.create(product_id=product_id, **self.validated_data)
        return self.instance

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many = True, read_only = True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'slug',
            'inventory',
            'unit_price',
            'images',
        ]

class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )

    class Meta:
        model = CartItem
        fields = [
            'product',
            'quantity',
            'total_price'
        ]
    
    def get_total_price(self, cartitem: CartItem) -> Decimal:
        return cartitem.product.unit_price * cartitem.quantity

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'quantity'
        ]

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No such product')
        return value

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']
        try:
            cartitem = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cartitem.quantity += quantity
            cartitem.save()
        except CartItem.DoesNotExist:
            cartitem = CartItem.objects.create(cart_id=cart_id, product_id=product_id, quantity=quantity)
        self.instance = cartitem
        return cartitem

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    def get_total_price(self, cart: Cart) -> Decimal:
        total_price = Decimal(0)
        for item in cart.items.all():
            total_price += item.quantity * item.product.unit_price
        return total_price

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'user_id',
            'phone',
            'birth_date',
            'membership',
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )

    class Meta:
        model = OrderItem
        fields = [
            'product',
            'quantity',
            'unit_price',
            'total_price',
        ]

    def get_total_price(self, orderitem: OrderItem) -> Decimal:
        return Decimal(orderitem.unit_price * orderitem.quantity)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only = True, many = True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'items',
            'total_price',
            'payment_status',
            'customer'
        ]

    def get_total_price(self, order: Order) -> Decimal:
        total_price = Decimal(0)
        for orderitem in order.items.all():
            total_price += orderitem.quantity * orderitem.unit_price
        return total_price

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(id=cart_id).exists():
            raise serializers.ValidationError("No cart with the given ID was found")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty.")
        return cart_id

    @transaction.atomic
    def save(self, **kwargs):
        customer = Customer.objects.get(user_id=self.context['user_id'])
        order = Order.objects.create(customer=customer)
        cartitems = CartItem.objects.select_related('product').\
            filter(cart_id=self.validated_data['cart_id'])
        orderitems = [
            OrderItem(
                order = order,
                product = item.product,
                quantity = item.quantity,
                unit_price = item.product.unit_price
            ) for item in cartitems
        ]
        orderitems = OrderItem.objects.bulk_create(orderitems)
        Cart.objects.filter(id=self.validated_data['cart_id']).delete()

        order_created.send_robust(self.__class__, order=order)

        return order
    
class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']