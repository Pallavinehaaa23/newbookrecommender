import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd
import random
import re
import os

# Download required resources (run only once)
nltk.download('vader_lexicon')
nltk.download('punkt')

# Initialize Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

# Genre mapping
genre_score_ranges = {
    "Comedy": (0.6, 1.0),
    "Romance": (0.5, 0.8),
    "Adventure": (0.4, 0.7),
    "Fantasy": (0.2, 0.5),
    "Self-Help": (0.3, 0.6),
    "Historical Fiction": (0.2, 0.5),
    "Science Fiction": (-0.1, 0.3),
    "Mystery": (-0.2, 0.2),
    "Thriller": (-0.5, -0.1),
    "Psychological Fiction": (-0.6, -0.2),
    "Dystopian": (-0.7, -0.3),
    "Horror": (-1.0, -0.6),
    "Tragedy": (-0.9, -0.5),
    "Dark Fiction": (-1.0, -0.7)
}

# Load dataset once
dataset_path = "books_1.Best_Books_Ever.csv"
df = pd.read_csv(dataset_path)

# --- Core Functions ---

def analyze_sentiment(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    vader_score = sia.polarity_scores(text)['compound']
    textblob_score = TextBlob(text).sentiment.polarity
    final_score = (vader_score + textblob_score) / 2
    return final_score

def compute_weighted_sentiment(responses):
    weights = [i+1 for i in range(len(responses))]
    weighted_sum = sum(analyze_sentiment(responses[i]) * weights[i] for i in range(len(responses)))
    total_weight = sum(weights)
    return weighted_sum / total_weight

def detect_user_mood(weighted_avg):
    if weighted_avg > 0.6:
        return "Very Positive 😃"
    elif 0.3 < weighted_avg <= 0.6:
        return "Positive 😊"
    elif 0 <= weighted_avg <= 0.3:
        return "Neutral 😐"
    elif -0.6 <= weighted_avg < -0.1:
        return "Negative 😞"
    else:
        return "Very Negative 😡"

def map_mood_to_genre(weighted_avg):
    valid_genres = []
    genre_weights = {}
    closest_genre = None
    min_distance = float("inf")

    for genre, (low, high) in genre_score_ranges.items():
        if low <= weighted_avg <= high:
            valid_genres.append(genre)
            genre_weights[genre] = 1 / (abs(weighted_avg - (low + high) / 2) + 0.01)
        distance = min(abs(weighted_avg - low), abs(weighted_avg - high))
        if distance < min_distance:
            min_distance = distance
            closest_genre = genre

    if valid_genres:
        selected_genre = max(genre_weights, key=genre_weights.get)
    else:
        selected_genre = closest_genre

    return selected_genre

def recommend_books(selected_genre, df, num_recommendations=10):
    if "genres" not in df.columns:
        return []

    filtered_books = df[df["genres"].str.contains(selected_genre, case=False, na=False)]

    if filtered_books.empty:
        return []

    book_list = filtered_books[["title", "author", "coverImg"]].values.tolist()
    random.shuffle(book_list)
    return book_list[:num_recommendations]

# --- Main Exported Function ---

def get_recommendations(responses):
    weighted_avg = compute_weighted_sentiment(responses)
    mood = detect_user_mood(weighted_avg)
    genre = map_mood_to_genre(weighted_avg)
    books = recommend_books(genre, df)

    return {
        "sentiment_score": round(weighted_avg, 2),
        "mood": mood,
        "genre": genre,
        "books": books
    }
