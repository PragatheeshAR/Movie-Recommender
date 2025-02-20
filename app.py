import pandas as pd
import streamlit as st
import pickle
import requests
import urllib.parse
import random


# Function to fetch poster from OMDB API
def fetch(title):
    # Ensure the title is encoded into bytes before passing to urllib.parse.quote
    encoded_title = urllib.parse.quote(title.encode('utf-8'))
    response = requests.get(f'https://www.omdbapi.com/?t={encoded_title}&apikey=6b1e5a0e')
    data = response.json()
    return data['Poster']


# Function to recommend movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = i[0]
        # Fetch poster through API
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch(movies.iloc[i[0]].title))
    return recommended_movies, recommended_movies_posters

def get_top_raters(selected_movie_name, num_users=5):
  # Filter the DataFrame for the specified film
  film_ratings = final_data[final_data['film_name'] == selected_movie_name]

  # Sort the filtered DataFrame by rating in descending order
  top_raters = film_ratings.sort_values(by='rating', ascending=False)

  # Extract the top 'num_users' usernames
  top_usernames = top_raters['user_name'].head(num_users).tolist()

  return top_usernames

def get_highly_rated_movies(top_usernames, min_rating=4.5, num_movies=5):
    # Filter the dataset for the top usernames
    user_ratings = final_data[final_data['user_name'].isin(top_usernames)]

    # Filter further for movies with ratings above the specified threshold
    highly_rated = user_ratings[user_ratings['rating'] >= min_rating]

    # Randomize the order of the movies
    randomized_movies = highly_rated.sample(frac=1, random_state=random.randint(1, 1000))

    # Extract the top 'num_movies' film names
    top_film_names = randomized_movies['film_name'].head(num_movies).tolist()

    return top_film_names


# Load data from pickle files
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

final = pickle.load(open('final_data.pkl', 'rb'))
final_data = pd.DataFrame(final)

similarity = pickle.load(open('similarity.pkl', 'rb'))
poster = pickle.load(open('poster.pkl', 'rb'))  # Assuming this contains a DataFrame with title and posterlink

st.title('WatchBuddy')

# User selects their favorite movie
selected_movie_name = st.selectbox('Enter your favorite movie', movies['title'].values)

if st.button("Recommend"):
    # Fetch recommendations
    names, posters = recommend(selected_movie_name)

    # First row: Recommended movies
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.code(names[0], language="text")
        st.image(posters[0])
    with col2:
        st.code(names[1], language="text")
        st.image(posters[1])
    with col3:
        st.code(names[2], language="text")
        st.image(posters[2])
    with col4:
        st.code(names[3], language="text")
        st.image(posters[3])
    with col5:
        st.code(names[4], language="text")
        st.image(posters[4])
    with col6:
        st.code(names[5], language="text")
        st.image(posters[5])

    # NEW ROW: Display highly rated movies of top raters
    st.title('You may also Like:')

    # Get top raters for the selected movie
    top_raters = get_top_raters(selected_movie_name, num_users=5)

    # Get highly rated movies from these top raters
    highly_rated_movies = get_highly_rated_movies(top_raters, min_rating=4.5, num_movies=5)

    # Create columns to display these movies and their posters
    top_raters_row = st.columns(len(highly_rated_movies))
    for idx, movie_name in enumerate(highly_rated_movies):
        poster_link = fetch(movie_name)  # Dynamically fetch the poster link
        with top_raters_row[idx]:
            st.code(movie_name, language="text")
            st.image(poster_link)

    # Second row: Display top 5 movies from the 'poster' DataFrame
    st.title('Our Top 5 Recommendations')

    second_row = st.columns(5)
    for idx, col in enumerate(second_row):
        if idx < len(poster):  # Ensure we don't exceed the number of rows in the poster DataFrame
            movie_title = poster.iloc[idx]['Series_Title']  # Get the movie title
            poster_link = fetch(movie_title)  # Dynamically fetch the poster link
            with col:
                st.code(movie_title, language="text")
                st.image(poster_link)

    st.success("Hope you like the recommendations!", icon="✅")


