from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, UpdateModelMixin
from store.filters import ProductFilter
from store.models import Cart, CartItem, Collection, Customer, OrderItem, Product, Review
from store.paginations import DefaultPagination
from store.serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CustomerSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer

# Create your views here.
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fileds = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            err_msg = "Product cannot be deleted because \
            it is in an order"
            return Response({'error': err_msg})
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            err_msg = "Collection cannot be deleted because \
            there are products belong to this collection"
            return Response({'error': err_msg})
        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    
    def get_queryset(self):
        return CartItem.objects.\
            filter(cart_id=self.kwargs['cart_pk']).\
            select_related('product')

class CustomerViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet
):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["GET", "PUT"])
    def me(self, request):
        user = request.user
        customer, _ = Customer.objects.get_or_create(user_id = user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        if request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)