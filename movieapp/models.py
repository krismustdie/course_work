from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
import os
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill, Thumbnail
from django.core.validators import FileExtensionValidator



class Movie(models.Model):
    id = models.AutoField(primary_key=True, unique=True) 
    tmdb_id = models.IntegerField()  
    is_Series = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    rating = models.FloatField()
    genre_ids = models.CharField(max_length=255) 
    episode_count = models.IntegerField(default=1)
    runtime = models.IntegerField()
    release_date = models.DateField()
    poster_path = models.CharField(max_length=255,blank=True)
    users_like = models.ManyToManyField(User,related_name='movies_liked',blank=True)
    users_watched = models.ManyToManyField(User,through='WatchedMovie', through_fields=('movie', 'user'),blank=True)
    
    
    class Meta:
        unique_together = ('tmdb_id', 'is_Series')
    
    def __str__(self):
        return self.title

class WatchedMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_at = models.DateField(default=None, blank=True, null=True)
    episodes_watched = models.IntegerField(default=1) 
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie} on {self.watched_at}"
    
def avatar_upload_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = ProcessedImageField(
        upload_to=avatar_upload_path,
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        options={'quality': 90},
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username

# Удаление старого аватара при обновлении
@receiver(pre_save, sender=Profile)
def delete_old_avatar(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_avatar = Profile.objects.get(pk=instance.pk).avatar
        except Profile.DoesNotExist:
            return
        else:
            new_avatar = instance.avatar
            if old_avatar and old_avatar != new_avatar:
                if os.path.isfile(old_avatar.path):
                    os.remove(old_avatar.path)

# Удаление аватара при удалении профиля
@receiver(post_delete, sender=Profile)
def delete_avatar_file(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)