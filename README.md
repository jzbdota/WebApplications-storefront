Yi Yang

yiy042@ucsd.edu

09/27/2023

python 3.10.9

MySQL 8.34

WSL for celery

docker

docker run -d -p 6379:6379 redis

celery -A storefront worker --loglevel=info

celery -A storefront beat

For smtp service
docker run --rm -it -p 3000:80 -p 2525:25 rnwood/smtp4dev

pip install django (4.2.5)

pip install django-debug-toolbar

pip install mysqlclient

pip install djangorestframework

pip install drf-nested-routers

pip install django-filter

pip install djoser

pip install djangorestframework_simplejwt

pip install django-cors-headers

pip install django-templated-mail

pip install redis

For monitoring celery:

pip install flower

For automated testing

pip install --dev pytest

pip install --dev pytest-django

Real-time tests, ptw

pip install --dev pytest-watch

Create fake data when creating model instances

pip install --dev model_bakery