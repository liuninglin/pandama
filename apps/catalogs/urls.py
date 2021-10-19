from django.urls import path
from apps.catalogs import views

urlpatterns = [
    path('test_asyncCall/', views.test_asyncCall, name='test_asyncCall'),
    path('test_redis/', views.test_redis, name='test_redis'),
    path('test_mongoDB/', views.test_mongoDB, name='test_mongoDB'),
    path('test_es/', views.test_es, name='test_es'),
]
