from django.contrib import admin
from .models import Movie, WatchedMovie

admin.site.register(WatchedMovie)
admin.site.register(Movie)
# Register your models here.
