import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load dataset
df = pd.read_csv("Dataset/books.csv")


# Prepare book text
df["Book_Text"] = (
    df["Title"] + " " +
    df["Subject"] + " " +
    df["Description"] + " " +
    df["Keywords"]
)

df["Book_Text"] = (
    df["Book_Text"]
    .str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)


# TF-IDF
vectorizer = TfidfVectorizer(stop_words="english")

tfidf_matrix = vectorizer.fit_transform(
    df["Book_Text"]
)


def detect_difficulty(query):

    query = query.lower()

    if any(word in query for word in [
        "beginner", "basic", "basics", "easy",
        "start", "starting"
    ]):
        return "Beginner"

    elif any(word in query for word in [
        "intermediate", "moderate"
    ]):
        return "Intermediate"

    elif any(word in query for word in [
        "advanced", "expert", "deep"
    ]):
        return "Advanced"

    return None


def detect_intent(query):

    query = query.lower()

    if any(word in query for word in [
        "exam", "examination", "test", "revision"
    ]):
        return "Exam Preparation"

    elif any(word in query for word in [
        "project", "project work", "implementation"
    ]):
        return "Project"

    elif any(word in query for word in [
        "research", "research paper", "research work"
    ]):
        return "Research"

    elif any(word in query for word in [
        "practice", "practical", "examples", "hands-on"
    ]):
        return "Practical Learning"

    elif any(word in query for word in [
        "learn", "learning", "understand", "study"
    ]):
        return "Learning"

    return "General Search"


def wants_practical(query):

    query = query.lower()

    practical_words = [
        "practical",
        "hands-on",
        "examples",
        "real world",
        "implementation",
        "projects"
    ]

    return any(
        word in query
        for word in practical_words
    )


def smart_recommend_books(user_query, top_n=5):

    query_vector = vectorizer.transform([user_query])

    similarity_scores = cosine_similarity(
        query_vector,
        tfidf_matrix
    )[0]

    results = df.copy()
    results["Similarity"] = similarity_scores
    results["Final_Score"] = results["Similarity"]

    difficulty = detect_difficulty(user_query)
    practical = wants_practical(user_query)
    intent = detect_intent(user_query)

    # Difficulty
    if difficulty:
        results.loc[
            results["Difficulty"] == difficulty,
            "Final_Score"
        ] += 0.20

    # Availability
    results.loc[
        results["Available"] == "Yes",
        "Final_Score"
    ] += 0.05

    # Practical preference
    if practical:

        for word in [
            "practical",
            "examples",
            "hands-on",
            "implementation",
            "projects"
        ]:

            mask = results["Book_Text"].str.contains(
                word,
                case=False,
                na=False
            )

            results.loc[mask, "Final_Score"] += 0.05

    # Intent
    if intent == "Exam Preparation":

        results.loc[
            results["Difficulty"] == "Beginner",
            "Final_Score"
        ] += 0.10

    elif intent == "Research":

        results.loc[
            results["Difficulty"] == "Advanced",
            "Final_Score"
        ] += 0.10

    elif intent in ["Project", "Practical Learning"]:

        for word in [
            "practical",
            "examples",
            "implementation",
            "hands-on",
            "project"
        ]:

            mask = results["Book_Text"].str.contains(
                word,
                case=False,
                na=False
            )

            results.loc[mask, "Final_Score"] += 0.08

    results = results.sort_values(
        by="Final_Score",
        ascending=False
    )

    return results.head(top_n)


def get_recommendations_with_confidence(
    user_query,
    top_n=5
):

    query_vector = vectorizer.transform(
        [user_query]
    )

    similarity_scores = cosine_similarity(
        query_vector,
        tfidf_matrix
    )[0]

    max_similarity = similarity_scores.max()

    if max_similarity < 0.10:
        return None, max_similarity

    recommendations = smart_recommend_books(
        user_query,
        top_n
    )

    return recommendations, max_similarity