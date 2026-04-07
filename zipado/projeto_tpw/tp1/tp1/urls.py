from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Isto diz ao Django: "Se o URL não for 'admin/', vai ver o que está em app/urls.py"
    path('', include('app.urls')),
]