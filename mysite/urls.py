from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("movieapp/", include("movieapp.urls")),
]

urlpatterns += [
    path('', RedirectView.as_view(url='/movieapp/', permanent=False)),
]

urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
]
