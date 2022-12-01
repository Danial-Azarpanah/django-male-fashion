from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("home.urls")),
    path('account/', include("account.urls"))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
