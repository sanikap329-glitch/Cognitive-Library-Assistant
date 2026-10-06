import streamlit as st

st.title("📚 Cognitive Library Assistant")
st.write("The application is working!")

import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import streamlit as st


# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv("Dataset/books.csv")


# ============================================================
# 2. PREPARE BOOK TEXT
# ============================================================

df["Book_Text"] = (
    df["Title"] + " " +
    df["Subject"] + " " +
    df["Description"] + " " +
    df["Keywords"]
)

df["Book_Text"] = df["Book_Text"].str.lower()

df["Book_Text"] = (
    df["Book_Text"]
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)


# ============================================================
# 3. TF-IDF MODEL
# ============================================================

vectorizer = TfidfVectorizer(stop_words="english")

tfidf_matrix = vectorizer.fit_transform(
    df["Book_Text"]
)


# ============================================================
# 4. DETECT DIFFICULTY
# ============================================================

def detect_difficulty(query):

    query = query.lower()

    if any(word in query for word in [
        "beginner",
        "basic",
        "basics",
        "easy",
        "start",
        "starting"
    ]):
        return "Beginner"

    elif any(word in query for word in [
        "intermediate",
        "moderate"
    ]):
        return "Intermediate"

    elif any(word in query for word in [
        "advanced",
        "expert",
        "deep"
    ]):
        return "Advanced"

    else:
        return None


# ============================================================
# 5. DETECT INTENT
# ============================================================

def detect_intent(query):

    query = query.lower()

    if any(word in query for word in [
        "exam",
        "examination",
        "test",
        "revision"
    ]):
        return "Exam Preparation"

    elif any(word in query for word in [
        "project",
        "project work",
        "implementation"
    ]):
        return "Project"

    elif any(word in query for word in [
        "research",
        "research paper",
        "research work"
    ]):
        return "Research"

    elif any(word in query for word in [
        "practice",
        "practical",
        "examples",
        "hands-on"
    ]):
        return "Practical Learning"

    elif any(word in query for word in [
        "learn",
        "learning",
        "understand",
        "study"
    ]):
        return "Learning"

    else:
        return "General Search"


# ============================================================
# 6. DETECT PRACTICAL PREFERENCE
# ============================================================

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


# ============================================================
# 7. UNDERSTAND QUERY
# ============================================================

def understand_query(query):

    return {
        "query": query,
        "difficulty": detect_difficulty(query),
        "intent": detect_intent(query),
        "practical_preference": wants_practical(query)
    }


# ============================================================
# 8. SMART RECOMMENDATION
# ============================================================

def smart_recommend_books(user_query, top_n=5):

    query_vector = vectorizer.transform([user_query])

    similarity_scores = cosine_similarity(
        query_vector,
        tfidf_matrix
    )[0]

    results = df.copy()

    results["Similarity"] = similarity_scores

    requested_difficulty = detect_difficulty(user_query)
    practical = wants_practical(user_query)
    intent = detect_intent(user_query)

    results["Final_Score"] = results["Similarity"]

    # Difficulty preference
    if requested_difficulty:

        results.loc[
            results["Difficulty"] == requested_difficulty,
            "Final_Score"
        ] += 0.20

    # Availability preference
    results.loc[
        results["Available"] == "Yes",
        "Final_Score"
    ] += 0.05

    # Practical preference
    if practical:

        practical_words = [
            "practical",
            "examples",
            "hands-on",
            "implementation",
            "projects"
        ]

        for word in practical_words:

            mask = results["Book_Text"].str.contains(
                word,
                case=False,
                na=False
            )

            results.loc[
                mask,
                "Final_Score"
            ] += 0.05

    # Intent-based ranking

    if intent == "Exam Preparation":

        results.loc[
            results["Difficulty"] == "Beginner",
            "Final_Score"
        ] += 0.10

    elif intent == "Project":

        project_words = [
            "project",
            "practical",
            "implementation",
            "hands-on",
            "examples"
        ]

        for word in project_words:

            mask = results["Book_Text"].str.contains(
                word,
                case=False,
                na=False
            )

            results.loc[
                mask,
                "Final_Score"
            ] += 0.08

    elif intent == "Research":

        results.loc[
            results["Difficulty"] == "Advanced",
            "Final_Score"
        ] += 0.10

    elif intent == "Practical Learning":

        practical_words = [
            "practical",
            "examples",
            "hands-on",
            "implementation"
        ]

        for word in practical_words:

            mask = results["Book_Text"].str.contains(
                word,
                case=False,
                na=False
            )

            results.loc[
                mask,
                "Final_Score"
            ] += 0.08

    # Sort recommendations

    results = results.sort_values(
        by="Final_Score",
        ascending=False
    )

    return results.head(top_n)


# ============================================================
# 9. EXPLAIN RECOMMENDATION
# ============================================================

def explain_recommendation(book, user_query):

    reasons = []

    query = user_query.lower()

    requested_difficulty = detect_difficulty(user_query)

    # Difficulty reason
    if requested_difficulty == book["Difficulty"]:

        reasons.append(
            f"matches your requested "
            f"{requested_difficulty.lower()} level"
        )

    # Availability reason
    if book["Available"] == "Yes":

        reasons.append(
            "currently available"
        )

    # Topic matching
    important_words = [
        "python",
        "data",
        "analysis",
        "machine learning",
        "sql",
        "database",
        "artificial intelligence",
        "deep learning",
        "network",
        "statistics"
    ]

    matched_words = []

    book_text = book["Book_Text"].lower()

    for word in important_words:

        if word in query and word in book_text:

            matched_words.append(word)

    if matched_words:

        reasons.append(
            "matches topics such as "
            + ", ".join(matched_words)
        )

    if not reasons:

        reasons.append(
            "has high similarity with your query"
        )

    return reasons


# ============================================================
# 10. CONFIDENCE CHECK
# ============================================================

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

    # No strong match
    if max_similarity < 0.10:

        return None, max_similarity

    recommendations = smart_recommend_books(
        user_query,
        top_n
    )

    return recommendations, max_similarity


# ============================================================
# 11. STREAMLIT PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Cognitive Library Assistant",
    page_icon="📚",
    layout="wide"
)


# ============================================================
# 12. APPLICATION TITLE
# ============================================================

st.title("📚 Cognitive Library Assistant")

st.write(
    "Ask a natural-language question and get intelligent "
    "book recommendations based on your topic, difficulty, "
    "intent, and preferences."
)


# ============================================================
# 13. USER QUERY
# ============================================================

st.subheader("🔎 Ask the Library Assistant")

user_query = st.text_input(
    "Enter your query:",
    placeholder=(
        "Example: I am a beginner and want to "
        "learn Python for data analysis"
    )
)


# ============================================================
# 14. RECOMMEND BUTTON
# ============================================================

if st.button("📚 Recommend Books"):

    if user_query.strip() == "":

        st.warning(
            "Please enter a library query."
        )

    else:

        # Understand query

        understanding = understand_query(
            user_query
        )

        # --------------------------------------------
        # Query Understanding
        # --------------------------------------------

        st.subheader("🧠 Query Understanding")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write("**Difficulty**")

            st.write(
                understanding["difficulty"]
                if understanding["difficulty"]
                else "Not specified"
            )

        with col2:

            st.write("**Intent**")

            st.write(
                understanding["intent"]
            )

        with col3:

            st.write("**Practical Preference**")

            st.write(
                "Yes"
                if understanding["practical_preference"]
                else "No"
            )

        # --------------------------------------------
        # Recommendations
        # --------------------------------------------

        st.subheader("📚 Recommended Books")

        recommendations, confidence = (
            get_recommendations_with_confidence(
                user_query,
                top_n=5
            )
        )

        # --------------------------------------------
        # Confidence
        # --------------------------------------------

        st.write(
            f"**Match Confidence:** "
            f"{confidence:.3f}"
        )

        # --------------------------------------------
        # No recommendation
        # --------------------------------------------

        if recommendations is None:

            st.warning(
                "No strongly matching books were found."
            )

            st.info(
                "Try asking about subjects such as "
                "Python, SQL, databases, machine learning, "
                "deep learning, statistics, or artificial intelligence."
            )

        # --------------------------------------------
        # Show recommendations
        # --------------------------------------------

        else:

            for i, (_, book) in enumerate(
                recommendations.iterrows(),
                start=1
            ):

                st.markdown(
                    f"### {i}. {book['Title']}"
                )

                st.write(
                    f"**Author:** {book['Author']}"
                )

                st.write(
                    f"**Subject:** {book['Subject']}"
                )

                st.write(
                    f"**Difficulty:** "
                    f"{book['Difficulty']}"
                )

                st.write(
                    f"**Available:** "
                    f"{book['Available']}"
                )

                st.write(
                    f"**Recommendation Score:** "
                    f"{book['Final_Score']:.3f}"
                )

                # Explanation

                reasons = explain_recommendation(
                    book,
                    user_query
                )

                st.info(
                    "💡 Why recommended: "
                    + "; ".join(reasons)
                )

                st.divider()