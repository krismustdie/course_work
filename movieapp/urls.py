from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("results/", views.results, name="results"),
    path("movie/<int:id>", views.movie, name="movie"),
    path("tv/<int:id>", views.tv, name="tv"),
    # path("movie/<int:id>/crew", views.crew, name="crew"),
    path("profile/<int:id>", views.profile, name="profile"),
    path("profile/watched", views.watched, name="watched"),
    path("profile/liked", views.liked, name="liked"),
    path("profile/<int:id>/stats/", views.stats, name="stats"),
    path("profile/journal", views.journal, name="journal"),
    path("profile/edit/profile", views.edituserinfo, name="editprofile"),
    path("profile/edit/password", views.edituserpass, name="editpass"),
    path("registration", views.registration, name="registration"),
    path("addtofav/", views.addtofav, name="addtofav"),
    path("addtowatched/", views.addtowatched, name="addtowatched"),
    path("movie/<int:id>/journal", views.addtojournal, name="addtojournal"),
]

from django.views.generic import RedirectView
urlpatterns += [
    path("profile/", RedirectView.as_view(url='profile/watched', permanent=False)),
]