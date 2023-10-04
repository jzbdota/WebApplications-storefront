from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSET)
router.register('collections', views.CollectionViewSet)

urlpatterns = [
    path("", include(router.urls))
]