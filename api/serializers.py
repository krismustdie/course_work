from rest_framework import serializers
from django.contrib.auth.models import User
from movieapp.models import WatchedMovie, Movie, Profile
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Avg, Count, Min, Sum

class UserWatchStatsSerializer(serializers.ModelSerializer):
    watchtime = serializers.SerializerMethodField()
    movies_count = serializers.SerializerMethodField()
    series_count = serializers.SerializerMethodField()
    genre_counts = serializers.SerializerMethodField()
    episodes_count = serializers.SerializerMethodField()
    active_days = serializers.SerializerMethodField()
    weekdays_count = serializers.SerializerMethodField()
    timespan = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'watchtime', 
            'movies_count',
            'series_count',
            'genre_counts',
            'episodes_count',
            'active_days',
            'weekdays_count',
            'timespan'
        ]
        read_only_fields = [
            'id', 
            'username', 
            'watchtime', 
            'movies_count',
            'series_count',
            'episodes_count',
            'genre_counts'
        ]

    def get_queryset(self, obj):
        request = self.context.get('request')
        timespan = request.query_params.get('timespan', 'all_time') if request else 'all_time'
        
        queryset = WatchedMovie.objects.filter(user=obj).select_related('movie')
        
        now = datetime.now().date()
        if timespan == 'month':
            start_date = now - timedelta(weeks=4)
            queryset = queryset.filter(watched_at__gte=start_date)
        elif timespan == 'halfyear':
            start_date = now - relativedelta(months=6)
            queryset = queryset.filter(watched_at__gte=start_date)
        elif timespan == 'year':
            start_date = now - relativedelta(months=12)
            queryset = queryset.filter(watched_at__gte=start_date)
        
        return queryset

    def get_watchtime(self, obj):
        queryset = self.get_queryset(obj)
        
        total_minutes = 0
        for watched in queryset:
            total_minutes += watched.movie.runtime * watched.movie.episode_count
            
        return total_minutes

    def get_movies_count(self, obj):
        queryset = self.get_queryset(obj)
        return queryset.filter(movie__is_Series=False).count()

    def get_series_count(self, obj):
        queryset = self.get_queryset(obj).filter(movie__is_Series=True)
        total = 0
        for watched in queryset:
            if watched.episodes_watched==watched.movie.episode_count:
                total+=1
        return total

    def get_genre_counts(self, obj):
        queryset = self.get_queryset(obj)
        genre_counter = ''
        for watched in queryset:
            if watched.movie.genre_ids!='':
                genre_counter += watched.movie.genre_ids+','
        
        return genre_counter
    
    def get_episodes_count(self, obj):
        queryset = self.get_queryset(obj).filter(movie__is_Series=True)
        return queryset.aggregate(res=Sum("episodes_watched", default=0)).get("res")
    
    def get_active_days(self, obj):
        queryset = self.get_queryset(obj)
        # Фильтруем записи, где watched_at не None и получаем уникальные даты
        distinct_dates = queryset.exclude(watched_at__isnull=True).dates('watched_at', 'day').count()
        return distinct_dates

    def get_weekdays_count(self, obj):
        queryset = self.get_queryset(obj)
        
        # Инициализируем словарь для хранения минут по дням недели (0=Понедельник, 6=Воскресенье)
        weekdays = {i: 0 for i in range(7)}
        
        for watched in queryset.exclude(watched_at__isnull=True):  # Исключаем записи без даты
            weekday = watched.watched_at.weekday()
            runtime = watched.movie.runtime
            if watched.movie.is_Series:
                runtime *= watched.episodes_watched
            weekdays[weekday] += runtime
        
        return weekdays
    
    

class UserSearchSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']
    
    def get_avatar(self, obj):
        profile = Profile.objects.get(user=obj)
        if profile.avatar:
            return self.context['request'].build_absolute_uri(profile.avatar.url)
        return None

class WatchedMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchedMovie
        fields = ['movie', 'watched_at', 'episodes_watched']

class MovieSerializer(serializers.ModelSerializer):
    is_liked = serializers.SerializerMethodField()
    is_watched = serializers.SerializerMethodField()
    
    class Meta:
        model = Movie
        fields = ['id', 'tmdb_id', 'is_Series', 'title', 'rating', 'genre_ids', 
                  'episode_count', 'runtime', 'release_date', 'poster_path',
                  'is_liked', 'is_watched']
    
    def get_is_liked(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.users_like.filter(id=user.id).exists()
    
    def get_is_watched(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and obj.users_watched.filter(id=user.id).exists()