from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.db.models.aggregates import Count
from django.http.request import HttpRequest
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models
# Google django modeladmin for details

# Register your models here.
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = reverse('admin:store_product_changelist') + "?" + \
            urlencode({'collection__id' : str(collection.id)})
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
        
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            products_count = Count('product')
        )
# In the admin site
# to rename the collections, in the model, redefine __str__ method
# to sort the collections, def class Meta in the model
# or do it in the custom admin class, ordering =

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    low_inventory = '<10'

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            (self.low_inventory, 'Low'),
        ]
    
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == self.low_inventory:
            return queryset.filter(inventory__lt=10)

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status', 
                    'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 100
    list_select_related = ['collection']
    ordering = ['title']

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders')
    def orders(self, customer):
        url = reverse('admin:store_order_changelist') + "?" + \
            urlencode({'customer__id' : str(customer.id)})
        return format_html('<a href="{}">{} orders</a>', url, customer.orders)
        
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).annotate(
            orders = Count('order')
        )

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'payment_status']
    list_editable = ['payment_status']
    ordering = ['id']
    list_select_related = ['customer']
    # if one wants to sort it by name, def class Meta in Customer Model
    def customer_name(self, order):
        customer = order.customer
        return customer.first_name + ' ' + customer.last_name