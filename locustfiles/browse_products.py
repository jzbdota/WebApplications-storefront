from random import randint
from locust import HttpUser, task, between

class WebSiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def view_products(self):
        collection_id = randint(2, 6)
        url = f'/store/products/?collection_id={collection_id}'
        self.client.get(url, name='/store/products')
    
    @task(4)
    def view_product(self):
        product_id = randint(1, 1000)
        url = f'/store/products/{product_id}'
        self.client.get(url, name='/store/products/:id')
    
    @task(1)
    def add_to_cart(self):
        product_id = randint(1, 10) # wanna try adding repeated products
        url = f'/store/carts/{self.cart_id}/items/'
        self.client.post(url, 
                         name='/store/carts/items',
                         json={'product_id': product_id,
                               'quantity': 1})
    
    @task(10)
    def say_hello(self):
        self.client.get('/playground/hello/')

    def on_start(self):
        response = self.client.post('/store/carts/')
        result = response.json()
        self.cart_id = result['id']