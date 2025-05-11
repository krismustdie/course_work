from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("movieapp/", include("movieapp.urls")),
    path('api/', include('api.urls')),
]

urlpatterns += [
    path('', RedirectView.as_view(url='/movieapp/', permanent=False)),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)