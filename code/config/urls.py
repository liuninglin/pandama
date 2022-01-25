"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.commons.views_commons import CommonErrorPageViews

urlpatterns = [
    # path('', CustomerPageViews.store_customers_home_page, name='store_customers_home_page'),
    # path('admin/', admin.site.urls),
    
    path('', include('apps.commons.urls')),
    path('catalogs/', include('apps.catalogs.urls')),
    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('customers/', include('apps.customers.urls')),
    path('carts/', include('apps.carts.urls')),
]

handler404 = CommonErrorPageViews.error_404
handler500 = CommonErrorPageViews.error_500
handler403 = CommonErrorPageViews.error_403
handler400 = CommonErrorPageViews.error_400