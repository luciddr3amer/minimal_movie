import requests
from flask import Flask, render_template, request, redirect, url_for
from config import API_KEY

api_key = API_KEY

app = Flask(__name__)


def get_category_name(category_id):
    url = f'https://api.themoviedb.org/3/genre/movie/list?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['genres']
    for i in result:
        if i['id'] == category_id:
            return i['name']


def get_images(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'/images?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['backdrops']
    return result

def get_network_url(network_id):
    url = 'https://api.themoviedb.org/3/network/'+str(network_id)+'?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['homepage']
    return result


def get_movie_runtime(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['runtime']
    # convert runtime to hours and minutes
    hours = result // 60
    minutes = result % 60
    return f'{hours}h {minutes}m'


def get_trending():
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    return result


def get_youtube_video(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'/videos?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    for i in result:
        if i['site'] == 'YouTube':
            youtube_video = i['key']
            url = 'https://www.youtube.com/watch?v='+youtube_video
            return url


def embeded_youtube(movie_id):
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'/videos?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    youtube_video_key = result[-1]['key']
    # you_url = f'https://www.youtube.com/embed/{youtube_video_key}?autoplay=1&mute=1'
    you_url = f'https://www.youtube.com/watch?v={youtube_video_key}'
    return you_url


def get_ids():
    url = 'https://api.themoviedb.org/3/trending/all/day?api_key='+api_key
    response = requests.get(url)
    r = response.json()
    result = r['results']
    ids = []
    for i in result:
        ids.append(i['id'])
    return ids


@app.route('/')
def index():
    # try:
    trending = get_trending()
    # get all trending movie ids
    movie_ids = [movie['id'] for movie in trending]
    # get youtube video for each movie
    # youtube_videos = [get_youtube_video(
    #     movie_id) for movie_id in movie_ids]

    # # add youtube video to trending movie
    # for i in range(len(trending)):
    #     #     trending[i]['youtube_video'] = youtube_videos[i]
    # except:
    #     pass

    return render_template('index.html', trending=trending)




@app.route('/results', methods=['GET', 'POST'])
def results():
    #get search results of both movies and tv shows
    if request.method == 'POST':
        search = request.form['movie_name']
        url = 'https://api.themoviedb.org/3/search/multi?api_key='+api_key+'&query='+search
        response = requests.get(url)
        r = response.json()
        result = r['results']
        for i in result:
            if i['media_type'] == 'movie':
                i['media_type'] = 'Movie'

            elif i['media_type'] == 'tv':
                i['media_type'] = 'TV Show'    

                
                

        return render_template('search_results.html', result=result)



    # if request.method == 'POST':
    #     search = request.form['movie_name']
    #     url = 'https://api.themoviedb.org/3/search/movie?api_key='+api_key+'&query='+search
    #     response = requests.get(url)
    #     r = response.json()
    #     result = r['results']
    #     for i in result:
    #         genre = i['genre_ids']
    #         genre_name = [get_category_name(category_id)
    #                       for category_id in genre]
    #         i['genre_name'] = genre_name
        
    #     return render_template('search_results.html', result=result)


# get tv and movie details
@app.route('/details/<movie_id>')
def details(movie_id):
    id = get_ids()
    try:
        if int(movie_id) in id:
            url = 'https://api.themoviedb.org/3/movie/' + \
                str(movie_id)+'?api_key='+api_key
            response = requests.get(url)
            data = response.json()
            name = data['title']
            poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']
            year = data['release_date'].split('-')[0]
            overview = data['overview']
            rating = data['vote_average']
            vote_count = data['vote_count']
            try:
                trailer = embeded_youtube(movie_id)
            except:
                # dont show trailer if there is no trailer
                trailer = None
            category = data['genres']
            category_name = [i['name'] for i in category]

            runtime = get_movie_runtime(movie_id)

            return render_template('details.html', name=name, poster=poster, year=year, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name, runtime=runtime, trailer=trailer)
    except:
        url = 'https://api.themoviedb.org/3/tv/' + \
            str(movie_id)+'?api_key='+api_key
        response = requests.get(url)
        data = response.json()
        name = data['name']
        poster = 'https://image.tmdb.org/t/p/w500'+data['poster_path']
        # year = data['release_date']
        overview = data['overview']
        rating = data['vote_average']
        vote_count = data['vote_count']
        try:
            trailer = embeded_youtube(movie_id)
        except:
                # dont show trailer if there is no trailer
            trailer = None
        category = data['genres']
        category_name = [i['name'] for i in category]
        episodes = data['number_of_episodes']
        network = data['networks']
        nietwork_id= [i['id'] for i in network]
        for i in nietwork_id:
            network_link = get_network_url(i)


        
        



        return render_template('details.html', name=name, poster=poster, overview=overview, rating=rating, vote_count=vote_count, category_name=category_name,episodes=episodes,trailer=trailer, network=network, network_link=network_link)


@app.route('/results/movie/<movie_id>')
def moviescreen(movie_id):
    movie_id = movie_id
    url = 'https://api.themoviedb.org/3/movie/' + \
        str(movie_id)+'?api_key='+api_key
    response = requests.get(url)
    data = response.json()
    poster = data['poster_path']
    image_url = 'https://image.tmdb.org/t/p/w500{}'.format(poster)
    movie_name = data['title']
    year = data['release_date'].split('-')[0]
    overview = data['overview']
    rating = data['vote_average']
    vote_count = data['vote_count']
    try:
        trailer = embeded_youtube(movie_id)
    except:
        # dont show trailer if there is no trailer
        trailer = None
    category = data['genres']
    category_name = [i['name'] for i in category]

    runtime = get_movie_runtime(movie_id)

    return render_template('movie_details.html', movie_name=movie_name, category_name=category_name, image_url=image_url, year=year, overview=overview, rating=rating, vote_count=vote_count, runtime=runtime, trailer=trailer)


@app.route('/results/tv/<movie_id>')
def tvscreen(movie_id):
    movie_id = movie_id
    url = 'https://api.themoviedb.org/3/tv/' + \
        str(movie_id)+'?api_key='+api_key
    response = requests.get(url)
    data = response.json()
    poster = data['poster_path']
    image_url = 'https://image.tmdb.org/t/p/w500{}'.format(poster)
    movie_name = data['name']
    # year = data['release_date']
    overview = data['overview']
    rating = data['vote_average']
    vote_count = data['vote_count']
    try:
        trailer = embeded_youtube(movie_id)
    except:
        # dont show trailer if there is no trailer
        trailer = None
    category = data['genres']
    category_name = [i['name'] for i in category]
    episodes = data['number_of_episodes']
    network = data['networks']
    nietwork_id= [i['id'] for i in network]
    for i in nietwork_id:
        network_link = get_network_url(i)

    return render_template('tv_details.html', movie_name=movie_name, category_name=category_name, image_url=image_url, overview=overview, rating=rating, vote_count=vote_count, episodes=episodes, trailer=trailer, network=network, network_link=network_link)
    

    






if __name__ == '__main__':
    app.run(debug=True)
