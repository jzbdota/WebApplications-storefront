from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem, Collection, Customer, Product, Review

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'unit_price'
        ]
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'slug',
            'inventory',
            'unit_price',
        ]

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    products_count = serializers.IntegerField(read_only=True)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']
    
    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            'product',
            'quantity',
            'total_price'
        ]
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )
    def get_total_price(self, cartitem: CartItem) -> Decimal:
        return cartitem.product.unit_price * cartitem.quantity

class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'quantity'
        ]
        
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No such product')
        return value

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_id = self.context['cart_id']

        cartitem = CartItem.objects.get_or_create(cart_id=cart_id, product_id=product_id)
        cartitem.quantity += quantity
        self.instance = cartitem
        return cartitem.save()

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )

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
    # user_id = serializers.IntegerField()