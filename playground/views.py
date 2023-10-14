import requests
import logging
from django.shortcuts import render
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

class HelloView(APIView):
    def get(self, request):
        try:
            logger.info('Calling httpbin')
            response = requests.get('https://httpbin.org/delay/2')
            logger.info('Received the Response')
        except requests.ConnectionError:
            logger.critical('httpbin is off')
        data = response.json()
        return render(request, 'hello.html', {'name': data})