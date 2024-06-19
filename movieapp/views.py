from io import StringIO
import matplotlib.pyplot as plt
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Min, Sum
from django.db.models.functions import ExtractYear, ExtractMonth
import requests
from random import choice
from .forms import SignUpForm
from .models import Movie, WatchedMovie
from datetime import *
import os
from dotenv import load_dotenv

load_dotenv()
__genres = {28: "боевик", 12: "приключения", 16: "мультфильм", 35: "комедия", 80: "криминал", 99: "документальный", 18: "драма", 10751: "семейный", 14: "фэнтези", 36: "история",
            27: "ужасы", 10402: "музыка", 9648: "детектив", 10749: "мелодрама", 878: "фантастика", 10770: "телевизионный фильм", 53: "триллер", 10752: "военный", 37: "вестерн"}
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}
local_lang = "ru"

def index(request):
    random_genre = choice(list(__genres.items()))
    url_popular = f"https://api.themoviedb.org/3/movie/popular?language={
        local_lang}"
    url_random = f"https://api.themoviedb.org/3/discover/movie?language={
        local_lang}&page=1&sort_by=sort_by=vote_average.desc&with_genres={random_genre[0]}"
    url_soon = f"https://api.themoviedb.org/3/movie/upcoming?language={
        local_lang}"
    popular = []
    random_best = []
    soon = []
    for movie in requests.get(url_popular, headers=headers).json()["results"]:
        try:
            popular.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
        except:
            popular.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})
    for movie in requests.get(url_random, headers=headers).json()["results"]:
        try:
            random_best.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
        except:
            random_best.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})
        
    for movie in requests.get(url_soon, headers=headers).json()["results"]:
        try:
            soon.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
        except:
            soon.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})
    return render(request, 'index.html', {
        "popular": popular,
        "randoms": random_best,
        "soon": soon,
        "random_genre": random_genre[1]
    })


def results(request):
    query = request.GET.get('q')
    prev_query = request.GET.get('prevq')
    if query == "":
        query = prev_query
    page = int(request.GET.get('page'))
    results = []
    if query:
        url_search = f"https://api.themoviedb.org/3/search/movie?&language={
            local_lang}&query={query}&page={page}"
        data = requests.get(url_search, headers=headers).json()
        for movie in data["results"]:
            try:
                results.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
            except:
                results.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})
        if len(results) < 1:
            return render(request, 'no_results.html', {"error": 1})
    else:
        return render(request, 'no_results.html', {"error": 2})
    total_results = data["total_results"]
    total_pages = data["total_pages"]
    pages = [page_num for page_num in range(
        max(1, page-3), min(page+3, int(total_pages))+1)]
    return render(request, 'results.html', {
        "results": results,
        "pages": pages,
        "cur_page": page,
        "total_pages": total_pages,
        "total_results": total_results,
        "query": query
    })

def movie(request, id):
    # retrieving info from tmdb  api
    url_movie = f"https://api.themoviedb.org/3/movie/{
        id}?language={local_lang}&append_to_response=recommendations,credits"
    movie_details = requests.get(url_movie, headers=headers).json()
    # saving movie to a db if it doesnt exist
    movie = Movie(
            tmdb_id=movie_details["id"],
            title=movie_details["title"],
            rating=movie_details["vote_average"],
            genre_ids=movie_details["genres"],
            runtime=movie_details["runtime"],
            release_date=movie_details["release_date"],
            poster_path=movie_details["poster_path"],)
    movie.save()
    
    # retrieving info from db watched/liked
    is_watched = False
    is_liked = False
    if request.user.is_authenticated:
        is_watched = movie.users_watched.contains(request.user)
        is_liked = movie.users_like.contains(request.user)
    # formatting info from api
    credits_data = movie_details["credits"]
    movie_cast = credits_data["cast"][0:8]
    producer = None
    director = None
    for person in credits_data["crew"]:
        if person["job"] == "Producer" and producer is None:
            producer = person
        elif person["job"] == "Director" and director is None:
            director = person
    movie_recs = []
    for movie in movie_details["recommendations"]["results"][:5]:
        try:
            movie_recs.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
        except:
            movie_recs.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})

    genres = ", ".join([i["name"] for i in movie_details["genres"]])
    return render(request, 'movie.html', {
        "movie": movie_details,
        "genres": genres,
        "cast": movie_cast,
        "director": director,
        "producer": producer,
        "recs": movie_recs,
        "credits": credits_data,
        "is_watched": is_watched,
        "is_liked": is_liked,
        "max_date": datetime.strftime(datetime.today(), "%Y-%m-%d")
    })

from django.contrib.auth.decorators import login_required
@login_required
def addtofav(request):
    try:
        movie_id = request.POST.get('id')
        movie = Movie.objects.get(pk=int(movie_id))
        if movie.users_like.contains(request.user):
            movie.users_like.remove(request.user)
        else:
            movie.users_like.add(request.user)
            if not movie.users_watched.contains(request.user):
                movie.users_watched.add(request.user)
        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'error'})

@login_required
def addtowatched(request):
    try:
        movie_id = request.POST.get('id')
        movie = Movie.objects.get(pk=int(movie_id))
        if movie.users_watched.contains(request.user):
            movie.users_like.remove(request.user)
            movie.users_watched.remove(request.user)
        else:
            movie.users_watched.add(request.user)
        return JsonResponse({'status': 'ok'})
    except:
        return JsonResponse({'status': 'error'})
    

@login_required
def addtojournal(request, id):
    WatchedMovie(user=request.user, movie=Movie.objects.get(
        pk=int(id)), watched_at=request.POST.get('date')).save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def profile(request):
    watched = Movie.objects.filter(users_watched__in=[request.user])
    liked = Movie.objects.filter(users_like__in=[request.user])
    return render(request, 'profile.html', {"liked": liked, "watched": watched})


def watched(request):
    watched = Movie.objects.filter(users_watched__in=[request.user]).distinct()
    return render(request, 'profile/watched.html', {"watched": watched})


def liked(request):
    liked = Movie.objects.filter(users_like__in=[request.user])
    return render(request, 'profile/liked.html', {"liked": liked})


def journal(request):
    movies = WatchedMovie.objects.select_related('movie').filter(
        user=request.user, watched_at__isnull=False).order_by('-watched_at')
    time = movies.annotate(year=ExtractYear('watched_at'), month=ExtractMonth(
        'watched_at')).values("year", "month")
    journal_bymonth = {}
    for period in time:
        journal_bymonth[f"{period["month"]}.{period["year"]}"] = []
    for entry in movies:
        journal_bymonth[f"{entry.watched_at.month}.{
            entry.watched_at.year}"].append(entry)
    return render(request, 'profile/journal.html', {"journal": journal_bymonth})


def get_timespan(start: datetime, end: datetime, timespan: str):
    if timespan == "month" or timespan == "halfyear":
        result = f"{start.strftime("%d.%m")}-{end.strftime("%d.%m")}"
    else:
        result = f"{start.strftime("%m.%y")}-{end.strftime("%m.%y")}"
    return result

from colour import Color
def stats(request, timespan):
    # Getting the watched info from db
    end = datetime.today()
    if timespan == "month":
        results = WatchedMovie.objects.filter(watched_at__gte=(
            end - timedelta(weeks=4)), user=request.user)
        start = end - timedelta(weeks=4)
    elif timespan == "halfyear":
        results = WatchedMovie.objects.filter(watched_at__gte=(
            end - timedelta(weeks=26)), user=request.user)
        start = end - timedelta(weeks=26)
    elif timespan == "year":
        results = WatchedMovie.objects.filter(watched_at__gte=(
            end - timedelta(days=365)), user=request.user)
        start = end - timedelta(days=365)
    else:
        results = WatchedMovie.objects.filter(
            user=request.user, watched_at__isnull=False)
        date = WatchedMovie.objects.filter(user=request.user, watched_at__isnull=False).aggregate(
            Min("watched_at"))['watched_at__min']
        try:
            start = datetime.combine(date, time())
        except:
            start = datetime.today()
    if len(results) <1:
        return render(request, 'profile/stats.html', {"message": "Нет"})
    # calculating the watchtime stats
    step = (end - start) / 12
    timestamps = [datetime.date(start + i*step) for i in range(12)]
    timestamps.append(end.date())
    watchtime_labels = []
    watchtime_count = []

    for i in range(1, 13):
        time_start = timestamps[i-1]
        time_end = timestamps[i]
        watchtime_labels.append(get_timespan(time_start, time_end, timespan))
        watchtime_count.append(WatchedMovie.objects.filter(watched_at__gte=time_start, watched_at__lte=time_end,
                                                           user=request.user).aggregate(Sum("movie__runtime"))['movie__runtime__sum'])

    # removing none from results
    for i in range(len(watchtime_count)):
        watchtime_count[i] = watchtime_count[i] if watchtime_count[i] else 0

    # creating the timewatch barchart
    bar_fig, bar_ax = plt.subplots()
    bar_ax.bar(watchtime_labels, watchtime_count, color="#655a7c")
    plt.xticks(rotation=20)
    bar_ax.grid( color ='grey',
        linestyle ='-.', linewidth = 0.5,
        alpha = 0.2)
    bar_ax.set_facecolor("#00000000")
    bar_fig.set_facecolor("#00000000")

    # calculating the genres stats
    genres_all = ""
    genres_labels = {}
    for entry in results:
        genres_all += entry.movie.genre_ids
    for value in __genres.values():
        if genres_all.count(value) != 0:
            genres_labels[value] = genres_all.count(value)

    # creating the piechart     
    pie_fig, pie_ax = plt.subplots()
    pie_ax.pie(genres_labels.values(), labels=genres_labels.keys(), colors=[str(col) for col in list(Color("#3b2f55").range_to(Color("#c6b3ef"),len(genres_labels)))])
    pie_fig.set_facecolor("#00000000")
    
    imgdata = StringIO()
    bar_fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    bar_graph = imgdata.getvalue()

    imgdata = StringIO()
    pie_fig.savefig(imgdata, format='svg')
    imgdata.seek(0)
    pie_graph = imgdata.getvalue()

    return render(request, 'profile/stats.html', {
        "total_time": results.aggregate(Sum("movie__runtime"))['movie__runtime__sum'],
        "total_count": results.aggregate(Count("movie"))['movie__count'],
        "total_genres": len(genres_labels),
        "bar_graph": bar_graph,
        "piechart": pie_graph,
        "stats": genres_labels,
    })

def registration(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            return redirect('/', {"new_user": new_user})
    else:
        user_form = SignUpForm()
    return render(request, 'registration/signup.html', {'user_form': user_form})


from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import UserEditForm

@login_required
def edituserinfo(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            update_session_auth_hash(request, user) 
            return redirect('/')
    else:
        user_form = UserEditForm(instance=request.user)
    return render(request, 'registration/profile_change.html', {'user_form': user_form})
 
@login_required
def edituserpass(request):
    if request.method == 'POST':
        pass_form = PasswordChangeForm(request.user, data=request.POST)
        if pass_form.is_valid():
            user = pass_form.save()
            update_session_auth_hash(request, user)
            return redirect('/')
    else:
        pass_form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {'pass_form': pass_form})