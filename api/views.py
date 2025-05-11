from rest_framework import generics, permissions
from django.contrib.auth.models import User
from movieapp.models import Movie, WatchedMovie, Profile
from .serializers import UserWatchStatsSerializer, UserSearchSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

class UserWatchStatsView(generics.RetrieveAPIView):
    serializer_class = UserWatchStatsSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(User, pk=user_id)
    
class ProfileSearchView(generics.ListAPIView):
    pagination_class = PageNumberPagination
    page_size = 15
    serializer_class = UserSearchSerializer
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if len(query) < 2:
            return Profile.objects.none()
        
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        return users