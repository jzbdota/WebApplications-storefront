from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from store.models import Collection, OrderItem, Product
from store.serializers import CollectionSerializer, ProductSerializer

# Create your views here.
class ProductViewSET(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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