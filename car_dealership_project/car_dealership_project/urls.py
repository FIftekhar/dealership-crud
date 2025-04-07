from django.contrib import admin
from django.urls import path, include
from dealership.views import redirect_favicon

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', redirect_favicon),
    path('', include('dealership.urls')),
]