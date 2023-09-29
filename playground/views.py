from django.shortcuts import render
from django.db.models import F
from store.models import Product, OrderItem, Order

# Create your views here.
def say_hello(request):
    queryset = Product.objects.filter(inventory=F('unit_price'))

    context = {
        'name' : 'Yi',
        'products': list(queryset)
    }
    return render(request, 'hello.html', context)