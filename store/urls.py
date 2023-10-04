from django.urls import include, path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewSET, basename='products')
router.register('collections', views.CollectionViewSet)

# child router
products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(products_router.urls))
]