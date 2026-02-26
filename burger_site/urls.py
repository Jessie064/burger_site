from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),   # Django built-in admin
    path('', include('restaurant.urls')),
]
