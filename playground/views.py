from django.shortcuts import render
from django.db.models import Q
from store.models import Product

# Create your views here.
def say_hello(request):
    queryset = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))
    context = {
        'name' : 'Yi',
        'products': list(queryset)
    }
    return render(request, 'hello.html', context)