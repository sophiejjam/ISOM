import json, requests, pprint as pr, time, pandas as pd

APIKey = "05ff55684cb55f443d41d5558c15d6bb"

def get_API():
    print('Please get your API key from https://developers.themoviedb.org/3/getting-started/introduction')
    print('Please enter your API key from TMDB: ', end='')
    API = input()
    return API


def get_MovieList(API):
    # This function will ask recent movies/TV shows users watched and liked.
    # Users will provide title of the movies/TV shows, and provide rating to them.

    print('> To recommend you movies, I need to know list of films and TV shows you enjoyed!')
    time.sleep(1.5)
    print('> More films you tell me, the better recommendation is going to be.''')
    time.sleep(1.5)
    print('> How many favorite films do you want to tell me: ', end='')
    while True:
        try:
            numberofObjects = input()
            numberofObjects = int(numberofObjects)
        except ValueError:
            print('> Please enter a number: ', end='')
            continue
        else:
            break

    # Taking titles of favorite films
    print('> Please enter the title of your favorite film one by one!')
    user_movieList = []
    user_movieID = []



    for i in range(numberofObjects):
        jsonData = {'total_results': 1}
        print('Name of the film (with spaces between words): ', end='')
        title_search = input()
        url = 'https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1&include_adult=true' % (
        API, title_search)
        response = requests.get(url)
        response.raise_for_status()
        jsonData = json.loads(response.text)

        if jsonData['total_results'] == 0:
            dummy_var = 0
            while dummy_var == 0:
                print("> There\'s no film with the title: \x1B[3m%s\x1b[23m. Can you please search again?" %(title_search))
                print('Name of the film (with spaces between words): ', end='')
                title_search = input()
                url = 'https://api.themoviedb.org/3/search/movie?api_key=%s&language=en-US&query=%s&page=1&include_adult=true' % (
                    API, title_search)
                response = requests.get(url)
                response.raise_for_status()
                jsonData = json.loads(response.text)

                if jsonData['total_results'] >= 1:
                    dummy_var = 1

        if jsonData['total_results'] > 1:
            print("> There are multiple films that match your search. Which is the one you're looking for?")
            print('Search Result:')
            title = []
            release_date = []
            overview = []  # plot
            movie_ID = []  # Unique number for a film

            for t in jsonData['results']:
                title.append(t['title'])
                try:
                    release_date.append(str(t['release_date']))
                except:
                    release_date.append('NA')
                overview.append(t['overview'])
                try:
                    movie_ID.append(t['id'])
                except:
                    movie_ID.append('NA')

            userDF = pd.DataFrame({'title': title,
                                   'release_date': release_date, 'movie_ID': movie_ID})

            pd.set_option("display.max_rows", None, "display.max_columns", None)

            # Verify_list is a Dataframe that contains the title and the release date of films that users selected
            verify_list = pd.DataFrame({'title': title,
                                        'release_date': release_date})
            verify_list.index.name = 'ID Number'
            # 'overview': overview})
            print(verify_list)
            print('> Please enter the ID number of a film you\'re looking for: ', end='')

            idNumber = int(input())
            title_df = userDF.get('title')
            id_df = userDF.get('movie_ID')
            user_movieList.append(title_df[idNumber])
            user_movieID.append(id_df[idNumber])

            # Creating a DataFrame that contains the titles and IDs for films
            user_response = pd.DataFrame({'Title': user_movieList, 'Movie ID': user_movieID})

        print(' Movies you\'re searching for: \x1B[3m%s\x1b[23m' % user_movieList)
        if len(user_movieList) != numberofObjects:
            print('> Okay, what\'s your other favorite film?')
    print(user_response)

    return user_response


def get_MovieRating(movie_DF):
    print('Now, please give rating for the movies you mentioned with digits between 1 to 10 (1-bad, 10-great)')
    user_rating = []
    movie_titles = movie_DF.get('Title')

    rating = 1

    for i in range(len(movie_titles)):
        print('> What is your rating for the film \x1B[3m%s\x1b[23m: ' % (movie_titles[i]), end='')
        while True:
            try:
                rating = input()
                rating = float(rating)
            except ValueError:
                print('> Please enter your rating from 1 to 10.')
                print('> What is your rating for the film \x1B[3m%s\x1b[23m: ' % (movie_titles[i]), end='')
                continue
            if rating < 1 or rating >10:
                print('> Please enter your rating from 1 to 10.')
                print('> What is your rating for the film \x1B[3m%s\x1b[23m: ' % (movie_titles[i]), end='')
            else:
                break
        user_rating.append(rating)

    rating_DF = pd.DataFrame({'User Rating': user_rating})
    DF = pd.concat([movie_DF, rating_DF], axis=1)

    return DF


def get_recommendation(API, userDF):
    # This function creates an initial recommendation list based on a user's favorite films

    ID_series = userDF.get('Movie ID')
    rating_series = userDF.get('User Rating')

    #4 lists that will be part of the recommended list DataFrame
    recommended_titles = []
    release_dates = []
    vote_average = []
    weighted_rating = []

    # Requesting recommendation using the API
    for i in range(len(ID_series)):
        url = 'https://api.themoviedb.org/3/movie/%s/recommendations?api_key=%s&language=en-US&page=1' %(ID_series[i],API)
        response = requests.get(url)
        response.raise_for_status()
        jsonData = json.loads(response.text)

        for t in jsonData['results']:
            recommended_titles.append(t['original_title'])
            release_dates.append(t['release_date'])
            vote_average.append(t['vote_average'])
            weighted_rating.append((float(t['vote_average'])+float(rating_series[i]))/2) # Weighting the rating other users voted based on the user's preference.

        recommended_DF = pd.DataFrame({'Title': recommended_titles,
                                       'Release date': release_dates,
                                       'Vote average': vote_average,
                                       'weighted rating': weighted_rating})

    return recommended_DF

def get_averageRating(userDF):
    # This function calculate the average rating of users' choice of favorite films.
    # The computed average will be used as a minimum rating for recommended films to pass the test.

    rating = userDF.get('User Rating')
    total_rating = 0

    for i in range(len(rating)):
        total_rating += float(rating[i])
    rating_average = total_rating / len(rating)

    return rating_average

def eliminate(recommended_DF, rating_average):
    #This function will delete movies in recommended_DF if weighted rating is less than average rating of favorite films
    delete = recommended_DF[recommended_DF['weighted rating'] < rating_average]

    return delete

def top_recommended (finalist_DF):
    finalist_DF = finalist_DF.sort_values(by = 'weighted rating', ascending = False)
    return finalist_DF

API = get_API()
movie_DF = get_MovieList(API)
userDF = get_MovieRating(movie_DF)
favorite_film_average = get_averageRating(userDF)
recommended_DF = get_recommendation(API, userDF)
finalist = eliminate(recommended_DF, favorite_film_average)
finalist = top_recommended(finalist)
print('> Generating list of recommended films...')
time.sleep(1.5)
print('> Here\'s the list of recommended films! I hope you enjoy :)')
time.sleep(1)
print('Result:')
pr.pprint(finalist.iloc[:,[0,1,3]])
print('*Weighted ratings are predicted ratings you\'ll give to the films.')
