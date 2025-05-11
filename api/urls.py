from django.urls import path, include
from .views import UserWatchStatsView, ProfileSearchView

urlpatterns = [
    path('user/<user_id>/stats/', UserWatchStatsView.as_view(), name='user-watchtime-stats'),
    path('profiles/search/', ProfileSearchView.as_view(), name='profile-search'),
]
