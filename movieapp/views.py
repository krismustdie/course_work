from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models.functions import ExtractYear, ExtractMonth
import requests
from .forms import ProfileEditForm, SignUpForm
from .models import Movie, Profile, WatchedMovie
from datetime import *
import os
from dotenv import load_dotenv
import matplotlib.colors as mcolors
import numpy as np

load_dotenv()
__genres = {28: "боевик", 12: "приключения", 16: "мультфильм", 35: "комедия", 80: "криминал", 99: "документальный", 18: "драма", 
            10751: "семейный", 14: "фэнтези", 36: "история", 27: "ужасы", 10402: "музыка", 9648: "детектив", 10749: "мелодрама", 
            878: "фантастика", 10770: "телевизионный фильм", 53: "триллер", 10752: "военный", 37: "вестерн", 10759:"Боевик и Приключения", 
            10762:"Детский", 10763:"Новости", 10764:"Реалити-шоу", 10765:"НФ и Фэнтези", 10766:"Мыльная опера", 10767:"Ток-шоу", 10768:"Война и Политика"}

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv('API_KEY')}"
}

API_LINK = os.getenv('API_LINK')

local_lang = "ru"

def index(request):
    url_popular = f"https://api.themoviedb.org/3/movie/popular?language={
        local_lang}"
    url_soon = f"https://api.themoviedb.org/3/movie/upcoming?language={
        local_lang}"
    popular = []
    soon = []
    for movie in requests.get(url_popular, headers=headers).json()["results"]:
        try:
            popular.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
        except:
            popular.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})
            
        
    for movie in requests.get(url_soon, headers=headers).json()["results"]:
        try:
            soon.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": movie["vote_average"]})
        except:
            soon.append({"tmdb_id": movie["id"], "title": movie["title"], "poster_path": movie["poster_path"], "rating": 0.0})
    return render(request, 'index.html', {
        "popular": popular,
        "soon": soon
    })

def results(request):
    query = request.GET.get('q')
    media_type = request.GET.get('mediatype')
    page = int(request.GET.get('page'))
    
    tmdb_results = []
    user_results = []
    
    if not query:
        return render(request, 'no_results.html', {"error": 2})
    
    if media_type != "users":
        url_search = f"https://api.themoviedb.org/3/search/{media_type}?&language={
            local_lang}&query={query}&page={page}"
        data = requests.get(url_search, headers=headers).json()
        for movie in data["results"]:
            tmdb_results.append({"tmdb_id": movie["id"], 
                            "title": f"{movie["title"] if media_type == "movie" else movie["name"]}", 
                            "poster_path": movie["poster_path"], 
                            "rating": movie["vote_average"] if movie["vote_average"] else 0.0, 
                            "is_Series": not media_type == "movie",
                            "type": "media"})
        total_results = data["total_results"]
        total_pages = data["total_pages"]
        pages = [page_num for page_num in range(
            max(1, page-3), min(page+3, int(total_pages))+1)]
    
    if len(query) >= 2:
        url_search = f"{API_LINK}profiles/search/?q={query}"
        user_results = requests.get(url_search).json()
    
    if not tmdb_results and not user_results:
        return render(request, 'no_results.html', {"error": 1})
        
    
    if media_type != "users":
        return render(request, 'results.html', {
            "query": query,
            "results": tmdb_results,
            "genres":__genres,
            "req": request,
            "pages": pages,
            "cur_page": page,
            "total_pages": total_pages,
            "total_results": total_results,
            "mediatype": media_type
        })
    return render(request, 'results.html', {
            "query": query,
            "results":  user_results,
            "req": request,
            "mediatype": media_type
        })
    
    

def get_info(mediatype, id, request):
    # retrieving info from tmdb  api
    url_movie = f"https://api.themoviedb.org/3/{mediatype}/{id}?language={local_lang}&append_to_response=recommendations,credits"
    movie_details = requests.get(url_movie, headers=headers).json()
    # saving movie to a db if it doesnt exist
    genres = ", ".join([i["name"] for i in movie_details["genres"]])
    genres_list = ",".join([str(i["id"]) for i in movie_details["genres"]])
    
    is_movie = mediatype == "movie"
    title_key = "title" if is_movie else "name"
    date_key = "release_date" if is_movie else "first_air_date"

    episode_runtime = movie_details.get("episode_run_time", [])
    average_runtime = (
        sum(episode_runtime) / len(episode_runtime) 
        if episode_runtime 
        else 40 
    )
    
    episode_count = 1 if is_movie else movie_details["number_of_episodes"]
    
    movie, created = Movie.objects.get_or_create(
        tmdb_id=movie_details["id"],
        is_Series=not is_movie,
        defaults={
            'title': movie_details[title_key],
            'rating': movie_details["vote_average"],
            'genre_ids': genres_list,
            'runtime': movie_details["runtime"] if is_movie else average_runtime,
            'release_date': movie_details[date_key],
            'poster_path': movie_details["poster_path"],
            'episode_count': episode_count
        }
    )

    if not created:
        update_fields = []
        if movie.rating != movie_details["vote_average"]:
            movie.rating = movie_details["vote_average"]
            update_fields.append('rating')
        if movie.release_date != movie_details[date_key]:
            movie.release_date = movie_details[date_key]
            update_fields.append('release_date')
        if movie.episode_count != episode_count:
            movie.episode_count = episode_count
            update_fields.append('episode_count')
        if update_fields:
            movie.save(update_fields=update_fields)
        
    movie_details["is_Series"] = not is_movie
    
    # retrieving info from db watched/liked
    is_watched = False
    is_liked = False
    if request.user.is_authenticated:
        is_watched = movie.users_watched.contains(request.user)
        is_liked = movie.users_like.contains(request.user)
    # formatting info from api
    credits_data = movie_details["credits"]
    movie_cast = credits_data["cast"][:5]
    movie_recs = []
    for rec_movie in movie_details["recommendations"]["results"][:5]:
        movie_recs.append({"tmdb_id": rec_movie["id"], "title": rec_movie[title_key], "release_date": rec_movie[date_key]})

    
    return render(request, 'movie.html', {
        "movie": movie_details,
        "id": movie.id,
        "episodes": episode_count,
        "title":movie_details[title_key],
        "release_date":movie_details[date_key],
        "runtime":movie_details["runtime"] if is_movie else average_runtime,
        "genres": genres,
        "cast": movie_cast,
        "recs": movie_recs,
        "credits": credits_data,
        "is_watched": is_watched,
        "is_liked": is_liked,
        "max_date": datetime.strftime(datetime.today(), "%Y-%m-%d")
    })

def tv(request, id):
    return get_info("tv", id, request)

def movie(request, id):
    return get_info("movie", id, request)
    
from django.contrib.auth.decorators import login_required
@login_required
def addtofav(request):
    try:
        movie_id = request.POST.get('id')
        print(movie_id)
        movie = Movie.objects.get(pk=int(movie_id))
        print(movie)
        if movie.users_like.contains(request.user):
            movie.users_like.remove(request.user)
        else:
            movie.users_like.add(request.user)
            if not movie.users_watched.contains(request.user):
                movie.users_watched.add(request.user)
        return JsonResponse({'status': 'ok'})
    except Exception as e: 
        print(e)
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
    except Exception as e: 
        print(e)
        return JsonResponse({'status': 'error'})
    

@login_required
def addtojournal(request, id):
    WatchedMovie(user=request.user, movie=Movie.objects.get(
        pk=int(id)), watched_at=request.POST.get('date')).save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def profile(request, id):
    watched = Movie.objects.filter(users_watched=id).distinct()
    liked = Movie.objects.filter(users_like=id) 
    user_profile = Profile.objects.get(user=int(id))
    return render(request, 'profile/new_profile.html', {"user_profile":user_profile,"liked": liked, "watched": watched})

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
        journal_bymonth[f"{entry.watched_at.month}.{entry.watched_at.year}"].append(entry)
    return render(request, 'profile/journal.html', {"journal": journal_bymonth})

def get_timespan(start: datetime, end: datetime, timespan: str):
    if timespan == "month" or timespan == "halfyear":
        result = f"{start.strftime("%d.%m")}-{end.strftime("%d.%m")}"
    else:
        result = f"{start.strftime("%m.%y")}-{end.strftime("%m.%y")}"
    return result

from io import BytesIO
import base64
from collections import Counter
from wordcloud import WordCloud
from django.shortcuts import render

def stats(request, id):
    timespan = request.GET.get("timespan")
    url_search = f"{API_LINK}user/{id}/stats/?timespan={timespan}"
    results = requests.get(url_search).json()
    
    # ids = [int(l) for l in results["genre_counts"].split(',') if l.strip()]
    # genre_counter = Counter(ids)
    # word_freq = {__genres[gid]: count for gid, count in genre_counter.items() if gid in __genres}
    
    # def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    #     base_color = mcolors.hex2color('#A5231D')
    #     variation = np.random.uniform(0.7, 1.3, 3) 
    #     return tuple(np.clip(base_color * variation, 0, 1)) 
    
    # # Генерируем облако в памяти
    # wordcloud = WordCloud(
    #     width=800,
    #     height=400,
    #     mode="RGBA",
    #     background_color=None,
    #     font_path=os.path.join(settings.STATIC_ROOT, 'fonts/RobotoFlex.ttf'),  # Важно: нужен шрифт с поддержкой кириллицы!
    #     color_func=lambda *args, **kwargs: (255,0,0),
    #     prefer_horizontal=0.8,
    #     collocations=False
    # ).generate_from_frequencies(word_freq)
    
    # # Конвертируем в base64 для вставки в HTML
    # img_buffer = BytesIO()
    # wordcloud.to_image().save(img_buffer, format='PNG')
    # img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    return render(request, 'profile/stats.html', {
        "stats": results,
        "timespan":timespan,
        # 'wordcloud_image': img_str,
        # "total_time": results.aggregate(Sum("movie__runtime"))['movie__runtime__sum'],
        # "total_count": results.aggregate(Count("movie"))['movie__count'],
        # "total_genres": len(genres_labels),
        # "bar_graph": bar_graph,
        # "piechart": pie_graph,
        # "stats": genres_labels,
    })

def registration(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save()
            Profile.objects.create(user=new_user)
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
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES )
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save()
            update_session_auth_hash(request, user) 
            return redirect(f'/movieapp/profile/{request.user.id}')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'registration/profile_change.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def edituserpass(request):
    if request.method == 'POST':
        pass_form = PasswordChangeForm(request.user, data=request.POST)
        if pass_form.is_valid():
            user = pass_form.save()
            update_session_auth_hash(request, user)
            return redirect(f'/movieapp/profile/{request.user.id}')
    else:
        pass_form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_change.html', {'pass_form': pass_form})