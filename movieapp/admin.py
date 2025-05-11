from django.contrib import admin
from .models import Movie, WatchedMovie, Profile

admin.site.register(WatchedMovie)
admin.site.register(Movie)
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar']
    raw_id_fields = ['user']