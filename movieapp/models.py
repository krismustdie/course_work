from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Movie(models.Model):
    tmdb_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    rating = models.FloatField()
    genre_ids = models.CharField(max_length=255) 
    runtime = models.IntegerField()
    release_date = models.DateField()
    poster_path = models.CharField(max_length=255,blank=True)
    users_like = models.ManyToManyField(User,related_name='movies_liked',blank=True)
    users_watched = models.ManyToManyField(User,through='WatchedMovie', through_fields=('movie', 'user'),blank=True)
    def __str__(self):
        return self.title

class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_at = models.DateField(default=None, blank=True)
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie.title} on {self.watched_at}"