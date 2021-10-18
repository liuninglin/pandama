from django.urls import path
from apps.catalogs import views

urlpatterns = [
    path('test/', views.tearDown, name='test'),
]
